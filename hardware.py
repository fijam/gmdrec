""" Talking to the hardware. Catching errors.

Currently three hardware revisions are supported:

    rev1: the original device with micro-usb in a plastic shell (MCP2221+AD5245)
    rev2: StemmaQT accessory (AD5245+CAT24C04)
    rev3a: double-sided PCB in rev2 form factor with a USB A cable (MCP2221+MCP4562)
    rev3b: single-sided PCB with micro-USB connector (MCP2221+MCP4562)
                * electrically like rev3a, same i2c address for MCP4562
"""
import logging
import time
import os
from settings import wipers

os.environ["BLINKA_MCP2221"] = "1"

#logging.basicConfig(level=logging.INFO)

try:
    import board
    import digitalio
    import busio
    i2c = busio.I2C(board.SCL, board.SDA)
    from adafruit_bus_device.i2c_device import I2CDevice
except RuntimeError:
    logging.warning("Titler not conneted to USB! \n")


def read_mcp_eeprom(address):
    # address range is 6 to 15
    result = bytearray(2)
    pot.write_then_readinto(bytes([(address & 15) << 4 | 12]), result)
    return int.from_bytes(result, 'big')


def read_24c04_eeprom(address):
    # address range is 1 to 10
    mem = I2CDevice(i2c, 0x50)
    result = bytearray(1)
    mem.write_then_readinto(bytes([address & 0xff]), result)
    return int.from_bytes(result, 'big')


def wipers_from_eeprom():
    wiper_list = ['Play', 'Left', 'Right', 'Pause', 'Stop', 'VolUp', 'TMark', 'Playmode', 'Display', 'Record']
    try:
        if eeprom == 'mcp':
            values = [read_mcp_eeprom(address) for address in range(6, 16)]
        if eeprom == '24c04':
            values = [read_24c04_eeprom(address) for address in range(1, 11)]
        if not eeprom:
            raise UserWarning

    except UserWarning:
        logging.critical('Please enter calibration data in settings.conf ! \n')
        raise SystemExit

    else:
        cal = dict(zip(wiper_list, values))
        logging.info(f"Calibration data found in {eeprom} eeprom: {cal}")
        return cal


def shutdown_pot_ad5245():
    pot.write(bytes([0x20 & 0xff, 0 & 0xff]))


def shutdown_pot_mcp4562():
    pot.write(bytes([0x40 & 0xff, 0xf9 & 0xff]))


def write_pot_ad5245(value):
    pot.write(bytes([0x00 & 0xff, value & 0xff]))


def write_pot_mcp4562(value):
    pot.write(bytes([0x00 & 0xff, value & 0xff]))
    pot.write(bytes([0x40 & 0xff, 0xff]))  # resume from shutdown


def is_rev3():
    """
    #rev3 was supposed to have the digipot on a different i2c address but doesn't so we need to detect it differently.
    - read status register (05h) on mcp4562
    - returns 10 bits (in 2 bytes)
    D8-D4: set to 1
    D3: currently writing to eeprom (should be 0)
    D2: is wiper lock for R network 1 engaged (should be 0)
    D1: is wiper lock for R network 0 engaged (should be 0)
    D0: is EEPROM write-protected (should be 0)
    0b111110000 = 0x01, 0xf0
    """
    result = bytearray(2)
    pot.write_then_readinto(bytes([(5 & 15) << 4 | 12]), result)
    return True if result == bytearray([0x01, 0xf0]) else False


def pulldown_on_data(state):
    if state:
        datapin = digitalio.DigitalInOut(board.G2)
        datapin.direction = digitalio.Direction.OUTPUT
        datapin.value = False  # False is logical 0
    else:
        datapin = digitalio.DigitalInOut(board.G2)
        datapin.direction = digitalio.Direction.INPUT


def push_button(button, timing, times, shutdown=True):
    for _ in range(times):
        write_to_pot(wipers[button])
        time.sleep(timing)
        if shutdown:
            shutdown_pot()
            time.sleep(timing)


def cleanup_exit():
    print('Cleaning up.')
    shutdown_pot()
    pulldown_on_data(False)
    print('Bye!')
    raise SystemExit


try:
    pot = I2CDevice(i2c, 0x2C)
    if is_rev3():
        logging.info('rev3 board connected')
        from adafruit_blinka.microcontroller.mcp2221 import mcp2221
        mcp2221.mcp2221.gp_set_mode(3, 0b001)  # GP3 LED_I2C
        write_to_pot = write_pot_mcp4562
        shutdown_pot = shutdown_pot_mcp4562
        eeprom = 'mcp'
    elif 44 in i2c.scan():
        write_to_pot = write_pot_ad5245
        shutdown_pot = shutdown_pot_ad5245
        if 80 in i2c.scan():
            logging.info('rev2 board connected')
            eeprom = '24c04'
        else:
            logging.info('rev1 board connected')
            eeprom = None
except NameError:
    eeprom = None
    pass
else:
    shutdown_pot()
    if not any(wipers.values()):
        wipers = wipers_from_eeprom()
