from typing import Generator

import serial
from datetime import datetime

from p1.converter import MeterReading, Converter


class NoDataException(Exception):
    pass


class Reader:
    def __init__(self, baudrate=115200, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN,
                 stopbits=serial.STOPBITS_ONE, xonxoff=0, rtscts=0, timeout=20, port="/dev/ttyUSB0",
                 data_timeout: int=60):
        ser = serial.Serial()
        ser.baudrate = baudrate
        ser.bytesize = bytesize
        ser.parity = parity
        ser.stopbits = stopbits
        ser.xonxoff = xonxoff
        ser.rtscts = rtscts
        ser.timeout = timeout
        ser.port = port

        ser.open()
        self._ser = ser
        self._converter = Converter()
        self.data_timeout = data_timeout

    def read_forever(self) -> Generator[MeterReading, None, None]:
        telegram = bytearray()
        last_read = None
        # The last line of a DSMR telegram starts with a '!' and contains the checksum
        end_of_telegram_mark = ord('!')

        while True:
            try:
                p1_raw = self._ser.readline()
                telegram.extend(p1_raw)
                print(f"Read line: {p1_raw}")

                now = datetime.now()
                # Every line should contain at least this many bytes
                if len(p1_raw) > 5:
                    last_read = now
                else:
                    if last_read and (now - last_read).total_seconds() > self.data_timeout:
                        raise NoDataException(f"No data received for {self.data_timeout} seconds")

                if len(p1_raw) < 1:
                    print("Skipping empty line")
                    continue

                if p1_raw[0] == end_of_telegram_mark:
                    # End of message
                    message = telegram.decode(encoding='utf-8', errors='replace')
                    yield self._converter.convert_p1_message(message), message
                    telegram.clear()
            except:
                self._ser.close()
                raise
