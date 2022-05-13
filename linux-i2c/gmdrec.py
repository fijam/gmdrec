import os
import fcntl

# Defined in linux/i2c-dev.h
I2C_SLAVE = 0x0703


class I2C(object):
    def __init__(self, filename):
        self.i2c = os.open(filename, os.O_RDWR)

    def __del__(self):
        self.close()

    def close(self):
        if self.i2c is not None:
            os.close(self.i2c)
        self.i2c = None

    def write(self, addr, data):
        res = fcntl.ioctl(self.i2c, I2C_SLAVE, addr)
        if res != 0:
            return ValueError(f'ioctl(I2C_SLAVE) returned {res}')
        res = os.write(self.i2c, data)
        if res != len(data):
            return ValueError(f'write(<{len(data)} bytes>) returned {res}')


class GMDRec_Rev2(I2C):
    WIPER_LIST = [
        "Play/Pause",
        "Prev/Rew",
        "Next/FFwd",
        "Pause/Group",
        "Stop",
        "Vol+",
        "TMark",
        "PlayMode",
        "Display",
        "Record",
    ]

    WIPER_I2C_ADDR = 0x2C
    EEPROM_I2C_ADDR = 0x50

    def __init__(self, filename):
        super().__init__(filename)
        self.wiper_values = {name: self.read_eeprom(i) for i, name in enumerate(self.WIPER_LIST)}

        # TODO: Derive this value from other eeprom values properly
        self.wiper_values['Vol-'] = 212 # for me, (stop = 219, vol+ = 204)

        self.shutdown_pot()

    def __del__(self):
        self.shutdown_pot()
        super().__del__()

    def shutdown_pot(self):
        self.write(self.WIPER_I2C_ADDR, bytes([0x20, 0x00]))

    def button_down(self, button):
        self.write_to_pot(self.wiper_values[button])

    def button_up(self, button):
        self.shutdown_pot()

    def write_to_pot(self, value):
        self.write(self.WIPER_I2C_ADDR, bytes([0x00, value]))

    def read_eeprom(self, index):
        self.write(self.EEPROM_I2C_ADDR, bytes([index + 1]))
        return os.read(self.i2c, 1)[0]


def find_i2c_dev():
    for filename in os.listdir('/sys/class/i2c-dev'):
        link_dest = os.readlink(os.path.join('/sys/class/i2c-dev', filename))
        # Example path (path should include the USB VID/PID somewhere):
        # '../../devices/pci0000:00/.../0003:04D8:00DD.000E/i2c-8/i2c-dev/i2c-8'
        if ':04d8:00dd' in link_dest.lower():
            return f'/dev/{filename}'
