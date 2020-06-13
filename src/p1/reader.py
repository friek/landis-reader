from typing import Generator

import serial

from p1.converter import MeterReading, Converter


class Reader:
    def __init__(self, baudrate=115200, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN,
                 stopbits=serial.STOPBITS_ONE, xonxoff=0, rtscts=0, timeout=20, port="/dev/ttyUSB0"):
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

    def read_forever(self) -> Generator[MeterReading, None, None]:
        message = ""

        while True:
            try:
                p1_raw = self._ser.readline()
                line = str(p1_raw, encoding="utf-8").strip()
                message += line + "\n"
                print(line)
                if len(line) < 1:
                    continue

                if line[0] == '!':
                    # End of message
                    yield self._converter.convert_p1_message(message), message
                    message = ""
            except:
                self._ser.close()
                raise
