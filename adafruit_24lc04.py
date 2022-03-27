# SPDX-FileCopyrightText: Copyright (c) 2021 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# This is a bastardized version of Adafruit's 24lc32 library.
# Adafruit is not interested in extending support to other EEPROM chips from
# the 24 family and I don't have the time to re-implement it so here we are.
# https://github.com/adafruit/Adafruit_CircuitPython_24LC32/issues/15

# imports
import time
from micropython import const

try:
    from typing import Optional, Union, Sequence
    from digitalio import DigitalInOut
    from busio import I2C
except ImportError:
    pass

_MAX_SIZE_I2C = const(0x1000)


class EEPROM:
    """
    Driver base for the EEPROM Breakout.

    :param int max_size: The maximum size of the EEPROM
    :param bool write_protect: Turns on/off initial write protection
    :param DigitalInOut wp_pin: (Optional) Physical pin connected to the ``WP`` breakout pin.
        Must be a ``DigitalInOut`` object.
    """

    def __init__(
        self,
        max_size: int,
        write_protect: bool = False,
        wp_pin: Optional[DigitalInOut] = None,
    ) -> None:
        self._max_size = max_size
        self._wp = write_protect
        self._wraparound = False
        if not wp_pin is None:
            self._wp_pin = wp_pin
            # Make sure write_prot is set to output
            self._wp_pin.switch_to_output()
            self._wp_pin.value = self._wp
        else:
            self._wp_pin = wp_pin

    @property
    def write_wraparound(self) -> bool:
        """Determines if sequential writes will wrapaound highest memory address
        (``len(EEPROM) - 1``) address. If ``False``, and a requested write will
        extend beyond the maximum size, an exception is raised.
        """
        return self._wraparound

    @write_wraparound.setter
    def write_wraparound(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError("Write wraparound must be 'True' or 'False'.")
        self._wraparound = value

    @property
    def write_protected(self) -> bool:
        """The status of write protection. Default value on initialization is
        ``False``.

        When a ``WP`` pin is supplied during initialization, or using
        ``write_protect_pin``, the status is tied to that pin and enables
        hardware-level protection.

        When no ``WP`` pin is supplied, protection is only at the software
        level in this library.
        """
        return self._wp if self._wp_pin is None else self._wp_pin.value

    def __len__(self) -> int:
        """The size of the current EEPROM chip. This is one more than the highest
        address location that can be read or written to.

        .. code-block:: python

            eeprom = adafruit_24lc32.EEPROM_I2C()
            # size returned by len()
            len(eeprom)
            # can be used with range
            for i in range(0, len(eeprom))
        """
        return self._max_size

    def __getitem__(self, address: Union[int, slice]) -> bytearray:
        """Read the value at the given index, or values in a slice.

        .. code-block:: python

            # read single index
            eeprom[0]
            # read values 0 thru 9 with a slice
            eeprom[0:9]
        """
        if isinstance(address, int):
            if not 0 <= address < self._max_size:
                raise ValueError(
                    "Address '{0}' out of range. It must be 0 <= address < {1}.".format(
                        address, self._max_size
                    )
                )
            buffer = bytearray(1)
            read_buffer = self._read_address(address, buffer)
        elif isinstance(address, slice):
            if address.step is not None:
                raise ValueError("Slice stepping is not currently available.")

            regs = list(
                range(
                    address.start if address.start is not None else 0,
                    address.stop if address.stop is not None else self._max_size,
                )
            )
            if regs[0] < 0 or (regs[0] + len(regs)) > self._max_size:
                raise ValueError(
                    "Address slice out of range. It must be 0 <= [starting address"
                    ":stopping address] < {0}.".format(self._max_size)
                )

            buffer = bytearray(len(regs))
            read_buffer = self._read_address(regs[0], buffer)

        return read_buffer

    def __setitem__(
        self, address: Union[int, slice], value: Union[int, Sequence[int]]
    ) -> None:
        """Write the value at the given starting index.

        .. code-block:: python

            # write single index
            eeprom[0] = 1
            # write values 0 thru 4 with a list
            eeprom[0:4] = [0,1,2,3]
        """
        if self.write_protected:
            raise RuntimeError("EEPROM currently write protected.")

        if isinstance(address, int):
            if not isinstance(value, int):
                raise ValueError("Data stored in an address must be an integer 0-255")
            if not 0 <= address < self._max_size:
                raise ValueError(
                    "Address '{0}' out of range. It must be 0 <= address < {1}.".format(
                        address, self._max_size
                    )
                )

            self._write(address, value, self._wraparound)

        elif isinstance(address, slice):
            if not isinstance(value, (bytes, bytearray, list, tuple)):
                raise ValueError(
                    "Data must be bytes, bytearray, list, "
                    "or tuple for multiple addresses"
                )
            if (address.start is None) or (address.stop is None):
                raise ValueError("Boundless slices are not supported")
            if (address.step is not None) and (address.step != 1):
                raise ValueError("Slice stepping is not currently available.")
            if (address.start < 0) or (address.stop > self._max_size):
                raise ValueError(
                    "Slice '{0}:{1}' out of range. All addresses must be 0 <= address < {2}.".format(  # pylint: disable=line-too-long
                        address.start, address.stop, self._max_size
                    )
                )
            if len(value) < (len(range(address.start, address.stop))):
                raise ValueError(
                    "Cannot set values with a list smaller than the number of indexes"
                )

            self._write(address.start, value, self._wraparound)

    def _read_address(self, address: int, read_buffer: bytearray) -> bytearray:
        # Implemented by subclass
        raise NotImplementedError

    def _write(
        self, start_address: int, data: Union[int, Sequence[int]], wraparound: bool
    ) -> None:
        # Implemened by subclass
        raise NotImplementedError


class EEPROM_I2C(EEPROM):
    """I2C class for EEPROM.

    :param ~busio.I2C i2c_bus: The I2C bus the EEPROM is connected to.
    :param int address: I2C address of EEPROM. Default address is ``0x50``.
    :param bool write_protect: Turns on/off initial write protection.
        Default is ``False``.
    :param wp_pin: (Optional) Physical pin connected to the ``WP`` breakout pin.
        Must be a ``DigitalInOut`` object.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        i2c_bus: I2C,
        address: int = 0x50,
        write_protect: bool = False,
        wp_pin: Optional[DigitalInOut] = None,
    ) -> None:
        from adafruit_bus_device.i2c_device import (  # pylint: disable=import-outside-toplevel
            I2CDevice as i2cdev,
        )

        self._i2c = i2cdev(i2c_bus, address)
        super().__init__(_MAX_SIZE_I2C, write_protect, wp_pin)

    def _read_address(self, address: int, read_buffer: bytearray) -> bytearray:
        write_buffer = bytearray(1)
        write_buffer[0] = address & 0xFF
        with self._i2c as i2c:
            i2c.write_then_readinto(write_buffer, read_buffer)
        return read_buffer

    def _write(
        self,
        start_address: int,
        data: Union[int, Sequence[int]],
        wraparound: bool = False,
    ) -> None:

        # Decided against using the chip's "Page Write", since that would require
        # doubling the memory usage by creating a buffer that includes the passed
        # in data so that it can be sent all in one `i2c.write`. The single-write
        # method is slower, and forces us to handle wraparound, but I feel this
        # is a better tradeoff for limiting the memory required for large writes.
        buffer = bytearray(2)
        if not isinstance(data, int):
            data_length = len(data)
        else:
            data_length = 1
            data = [data]
        if (start_address + data_length) > self._max_size:
            if wraparound:
                pass
            else:
                raise ValueError(
                    "Starting address + data length extends beyond"
                    " EEPROM maximum address. Use ``write_wraparound`` to"
                    " override this warning."
                )
        with self._i2c as i2c:
            for i in range(0, data_length):
                if not (start_address + i) > self._max_size - 1:
                    buffer[0] = (start_address + i) & 0xFF
                else:
                    buffer[0] = ((start_address + i) - self._max_size + 1) & 0xFF
                buffer[1] = data[i]
                i2c.write(buffer)

                time.sleep(0.005)

    # pylint: disable=no-member
    @EEPROM.write_protected.setter
    def write_protected(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError("Write protected value must be 'True' or 'False'.")
        self._wp = value
        if not self._wp_pin is None:
            self._wp_pin.value = value
