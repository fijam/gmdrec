""" Talking to the hardware. Catching errors.

Currently three hardware revisions are supported:

    rev1: the original device with micro-usb in a plastic shell (MCP2221+AD5245)
    rev2: StemmaQT accessory (AD5245+CAT24C04)
    rev3: double-sided PCB in rev2 form factor with a USB A cable (MCP2221+MCP4262)
"""
import logging
import time
import os
from settings import wipers

os.environ["BLINKA_MCP2221"] = "1"

# logging.basicConfig(level=logging.INFO)

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


def read_mcp_status():  # read status register at 05h to check for mcp4562
    result = bytearray(2)
    pot.write_then_readinto(bytes([(5 & 15) << 4 | 12]), result)
    return result


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
    if read_mcp_status() == bytearray([0x01, 0xf0]):  # 0b11110000
        logging.info('rev3 board connected')
        from adafruit_blinka.microcontroller.mcp2221 import mcp2221
        mcp2221.mcp2221.gp_set_mode(3, 0b001)
        write_to_pot = write_pot_mcp4562
        shutdown_pot = shutdown_pot_mcp4562
        shutdown_pot()
        eeprom = 'mcp'
    elif 44 in i2c.scan():
        write_to_pot = write_pot_ad5245
        shutdown_pot = shutdown_pot_ad5245
        shutdown_pot()
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
    if not any(wipers.values()):
        wipers = wipers_from_eeprom()
