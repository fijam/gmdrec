""" Talking to the hardware. Catching errors.

Currently three hardware revisions are supported:

    rev1: the original device with micro-usb in a plastic shell (MCP2221+AD5245)
    rev2: StemmaQT accessory (AD5245+CAT24C04)
    rev3: double-sided PCB in rev2 form factor with a USB A cable (MCP2221+MCP4262)
"""
import logging
import os
os.environ["BLINKA_MCP2221"] = "1"

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
    wiper_list = ['Play', 'Left', 'Right', 'Pause', 'Stop', 'VolUp', 'Tmark', 'Playmode', 'Display', 'Record']
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
        wipers = dict(zip(wiper_list, values))
        logging.info(f"Calibration data found in {eeprom} eeprom: {wipers}")
        return wipers


def shutdown_pot():
    if pot.device_address == 46:
        pot.write(bytes([0x40 & 0xff, 0xf9 & 0xff]))
    elif pot.device_address == 44:
        pot.write(bytes([0x20 & 0xff, 0 & 0xff]))


def write_to_pot(value):
    if pot.device_address == 46:
        pot.write(bytes([0x00 & 0xff, value & 0xff]))
        pot.write(bytes([0x40 & 0xff, 0xff]))  # resume from shutdown
    elif pot.device_address == 44:
        pot.write(bytes([0x00 & 0xff, value & 0xff]))


def pulldown_on_data(state):
    if state:
        datapin = digitalio.DigitalInOut(board.G2)
        datapin.direction = digitalio.Direction.OUTPUT
        datapin.value = False  # False is logical 0
    else:
        datapin = digitalio.DigitalInOut(board.G2)
        datapin.direction = digitalio.Direction.INPUT


try:
    if 46 in i2c.scan():
        logging.info('rev3 board connected')
        from adafruit_blinka.microcontroller.mcp2221 import mcp2221
        mcp2221.mcp2221.gp_set_mode(3, 0b001)
        pot = I2CDevice(i2c, 0x2E)
        shutdown_pot()
        eeprom = 'mcp'
    elif 44 in i2c.scan() and 80 in i2c.scan():
        logging.info('rev2 board connected')
        pot = I2CDevice(i2c, 0x2C)
        shutdown_pot()
        eeprom = '24c04'
    elif 44 in i2c.scan() and 80 not in i2c.scan():
        logging.info('rev1 board connected')
        pot = I2CDevice(i2c, 0x2C)
        shutdown_pot()
        eeprom = None
except NameError:
    eeprom = None
    pass
