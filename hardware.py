import os
os.environ["BLINKA_MCP2221"] = "1"

try:
    import board
    import digitalio
    import busio
    i2c = busio.I2C(board.SCL, board.SDA)
    from adafruit_bus_device.i2c_device import I2CDevice
except RuntimeError:
    print("Titler not conneted to USB! \n")


def read_mcp_eeprom(address):
    # address is 6 to 15
    result = bytearray(2)
    pot.write_then_readinto(bytes([(address & 15) << 4 | 12]), result)
    return int.from_bytes(result, 'big')


def read_24c04_eeprom(address):
    # address is 1 to 10
    mem = I2CDevice(i2c, 0x50)
    result = bytearray(1)
    mem.write_then_readinto(bytes([address & 0xff]), result)
    return int.from_bytes(result, 'big')


def wipers_from_eeprom():
    if eeprom == 'mcp':
        wipers = {'Play': read_mcp_eeprom(6),
                  'Left': read_mcp_eeprom(7),
                  'Right': read_mcp_eeprom(8),
                  'Pause': read_mcp_eeprom(9),
                  'Stop': read_mcp_eeprom(10),
                  'VolUp': read_mcp_eeprom(11),
                  'TMark': read_mcp_eeprom(12),
                  'Playmode': read_mcp_eeprom(13),
                  'Display': read_mcp_eeprom(14),
                  'Record': read_mcp_eeprom(15)}
        print(f"Calibration data found in eeprom: {wipers}")
        return wipers
    if eeprom == '24c04':
        wipers = {'Play': read_24c04_eeprom(1),
                  'Left': read_24c04_eeprom(2),
                  'Right': read_24c04_eeprom(3),
                  'Pause': read_24c04_eeprom(4),
                  'Stop': read_24c04_eeprom(5),
                  'VolUp': read_24c04_eeprom(6),
                  'TMark': read_24c04_eeprom(7),
                  'Playmode': read_24c04_eeprom(8),
                  'Display': read_24c04_eeprom(9),
                  'Record': read_24c04_eeprom(10)}
        print(f"Calibration data found in eeprom: {wipers}")
        return wipers
    else:
        print('Please enter calibration data in settings.conf ! \n')
        raise UserWarning


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


def pulldown_on_data():
    datapin = digitalio.DigitalInOut(board.G2)
    datapin.direction = digitalio.Direction.OUTPUT
    datapin.value = False


def reset_pulldown():
    datapin = digitalio.DigitalInOut(board.G2)
    datapin.direction = digitalio.Direction.INPUT


try:
    if 46 in i2c.scan():
        print('rev3 board connected')
        from adafruit_blinka.microcontroller.mcp2221 import mcp2221
        mcp2221.mcp2221.gp_set_mode(3, 0b001)
        pot = I2CDevice(i2c, 0x2E)
        shutdown_pot()
        eeprom = 'mcp'
    elif 44 in i2c.scan() and 80 in i2c.scan():
        print('rev2 board connected')
        pot = I2CDevice(i2c, 0x2C)
        shutdown_pot()
        eeprom = '24c04'
    elif 44 in i2c.scan() and 80 not in i2c.scan():
        print('rev1 board connected')
        pot = I2CDevice(i2c, 0x2C)
        shutdown_pot()
        eeprom = None
except NameError:
    pass
