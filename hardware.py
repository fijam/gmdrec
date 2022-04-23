import os

os.environ["BLINKA_MCP2221"] = "1"

try:
    import board
    import busio
    import adafruit_24lc04
    i2c = busio.I2C(board.SCL, board.SDA)
except RuntimeError:
    print("Titler not conneted to USB! \n")


def hardware_setup():
    # from adafruit_blinka.microcontroller.mcp2221 import mcp2221
    # mcp2221.mcp2221.gp_set_mode(3, 0b001)  # turn LED_I2C on
    from adafruit_bus_device.i2c_device import I2CDevice
    pot = I2CDevice(i2c, 0x2C)
    return pot


def eeprom_setup():
    try:
        eeprom = adafruit_24lc04.EEPROM_I2C(i2c)
        # see if it's really there
        eeprom[0]
        return eeprom
    except RuntimeError:
        return 0


def write_to_pot(value, pot):
    pot.write(bytes([0x00 & 0xff, value & 0xff]))


def shutdown_pot(pot):
    pot.write(bytes([0x20 & 0xff, 0 & 0xff]))
