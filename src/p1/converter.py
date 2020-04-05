import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple

import pendulum
from dataclasses_json import dataclass_json, config
from marshmallow import fields


class Tariff(Enum):
    NIGHT = 1
    DAY = 2


def date_encoder(s: pendulum.DateTime):
    if s is None:
        return None
    return s.to_iso8601_string()


def date_decoder(s: str):
    if s is None:
        return None
    return pendulum.parse(s)


@dataclass_json
@dataclass
class MeterReading:
    # Power meter model identification.
    model: str = ''
    # Version information for P1 output
    output_version: str = ''
    # Date/time of the power meter
    meter_time: pendulum.DateTime = field(
        default=None,
        metadata=config(
            encoder=date_encoder,
            decoder=date_decoder,
            mm_field=fields.DateTime(format='iso')
        )
    )
    # Serial number of the power meter.
    serial: str = ''
    # Total usage night tariff
    total_usage_night: float = 0.0
    # Total usage day tariff
    total_usage_day: float = 0.0
    # Total power delivered during day tariff
    total_energy_delivered_day: float = 0.0
    # Total power delivered during night tariff
    total_energy_delivered_night: float = 0.0
    # The currently active tariff
    active_tariff: Tariff = Tariff.DAY
    # Current power usage in kW
    current_power_usage: float = 0.0
    # Current power delivery in kW (back to the grid)
    current_power_delivery: float = 0.0
    # The total number of power interruptions registered
    num_power_interruptions: int = 0
    # The total number of long power interruptions registered
    num_long_power_interruptions: int = 0
    # Unknown
    power_failure_event_log: str = ''
    # Number of voltage sags in phase L1
    num_voltage_sags_phase_l1: int = 0
    # Number of voltage swells in phase L1
    num_voltage_swells_phase_l1: int = 0
    # Numeric message (?)
    message_numeric: int = 0
    # Textual message (?)
    message_text: str = None
    # Instantaneous current L1 in A resolution.
    instantaneous_current_l1: int = 0
    # Instantaneous active power L1 (+P) in W resolution
    instantaneous_active_power_draw_l1: float = 0.0
    # Instantaneous active power L1 (-P) in W resolution
    instantaneous_active_power_delivery_l1: float = 0.0
    # Number of devices on the M-Bus
    num_mbus_devices: int = 0
    # The serial number of the gas meter
    gas_meter_serial: str = None
    # The date/time of the last gas measurement
    gas_last_measurement: pendulum.DateTime = field(
        default=None,
        metadata=config(
            encoder=date_encoder,
            decoder=date_decoder,
            mm_field=fields.DateTime(format='iso')
        )
    )
    # Total usage of gas
    gas_usage_total: float = None


class Converter:
    __match_record__ = re.compile(r"^(?P<category>[0-9:\-.]+)\((?P<meta_or_value>[^)]+)\)(\((?P<value>.*)\))?$")
    __date_match__ = re.compile(
        r"^(?P<year>\d{2})(?P<mon>\d{2})(?P<day>\d{2})(?P<hr>\d{2})(?P<min>\d{2})(?P<sec>\d{2})(?P<time_type>[WS])")
    __float_match__ = re.compile(r"^(?P<value>\d+\.\d+)")

    def convert_p1_message(self, message) -> MeterReading:
        message_contents = self.__message_to_text__(message).split("\n")
        values = {}

        for reading in message_contents:
            if len(reading) == 0:
                continue
            elif reading[0] == '/':
                # Start of message.
                values['model'] = reading[1:]
            elif reading[0] == '!':
                # End of message.
                pass
            elif (record := self.__parse_reading__(reading)) is not None:
                self.__add_value_from_record__(record, values)

        return MeterReading(**values)

    def __add_value_from_record__(self, record: Tuple[str, str, str], values: dict):
        (category, meta_or_value, value) = record
        if (parse_info := self.__get_field_mapping__(category)) is None:
            return

        value_parser = parse_info['value_parser']
        value_dest = parse_info['value_dest']
        meta_parser = parse_info.get('meta_parser', None)
        meta_dest = parse_info.get('meta_dest', None)

        if meta_parser:
            values[meta_dest] = meta_parser(meta_or_value)
            values[value_dest] = value_parser(value)
        else:
            values[value_dest] = value_parser(meta_or_value)

    @staticmethod
    def __parse_reading__(message) -> Optional[Tuple[str, str, str]]:
        if (m := Converter.__match_record__.match(message)) is not None:
            return m.group('category'), m.group('meta_or_value'), m.group('value')
        return None

    @staticmethod
    def __message_to_text__(message) -> str:
        if isinstance(message, bytes):
            return str(message, encoding="utf-8")
        elif isinstance(message, str):
            return message

        raise ValueError("Unknown type to convert: " + message.__class__)

    @staticmethod
    def __parse_string__(value) -> str:
        return str(value)

    @staticmethod
    def __parse_int__(value) -> int:
        if len(value):
            return int(value)
        return 0

    @staticmethod
    def __timestamp__(value) -> Optional[pendulum.DateTime]:
        if (m := Converter.__date_match__.match(value)) is None:
            return None

        date_info = {
            'year': int('20' + m.group('year')),
            'month': int(m.group('mon')),
            'day': int(m.group('day')),
            'hour': int(m.group('hr')),
            'minute': int(m.group('min')),
            'second': int(m.group('sec')),
            'tz': 'CET',
        }

        return pendulum.datetime(**date_info)

        # return datetime(**date_info)

    @staticmethod
    def __parse_float__(value) -> float:
        if (m := Converter.__float_match__.match(value)) is None:
            return 0.0
        return float(m.group('value'))

    @staticmethod
    def __convert_tariff__(value) -> Optional[Tariff]:
        v = int(value)
        if v == 2:
            return Tariff.DAY
        elif v == 1:
            return Tariff.NIGHT

        return None

    @classmethod
    def __get_field_mapping__(cls, fld):
        field_mappings = {
            '1-3:0.2.8': {'value_parser': cls.__parse_string__, 'value_dest': 'output_version'},
            '0-0:1.0.0': {'value_parser': cls.__timestamp__, 'value_dest': 'meter_time'},
            '0-0:96.1.1': {'value_parser': cls.__parse_string__, 'value_dest': 'serial'},
            '1-0:1.8.1': {'value_parser': cls.__parse_float__, 'value_dest': 'total_usage_night'},
            '1-0:1.8.2': {'value_parser': cls.__parse_float__, 'value_dest': 'total_usage_day'},
            '1-0:2.8.1': {'value_parser': cls.__parse_float__, 'value_dest': 'total_energy_delivered_night'},
            '1-0:2.8.2': {'value_parser': cls.__parse_float__, 'value_dest': 'total_energy_delivered_day'},
            '0-0:96.14.0': {'value_parser': cls.__convert_tariff__, 'value_dest': 'active_tariff'},
            '1-0:1.7.0': {'value_parser': cls.__parse_float__, 'value_dest': 'current_power_usage'},
            '1-0:2.7.0': {'value_parser': cls.__parse_float__, 'value_dest': 'current_power_delivery'},
            '0-0:96.7.21': {'value_parser': cls.__parse_int__, 'value_dest': 'num_power_interruptions'},
            '0-0:96.7.9': {'value_parser': cls.__parse_int__, 'value_dest': 'num_long_power_interruptions'},
            '1-0:99.97.0': {'value_parser': cls.__parse_string__, 'value_dest': 'power_failure_event_log'},
            '1-0:32.32.0': {'value_parser': cls.__parse_int__, 'value_dest': 'num_voltage_sags_phase_l1'},
            '1-0:32.36.0': {'value_parser': cls.__parse_int__, 'value_dest': 'num_voltage_swells_phase_l1'},
            '0-0:96.13.1': {'value_parser': cls.__parse_int__, 'value_dest': 'message_numeric'},
            '0-0:96.13.0': {'value_parser': cls.__parse_string__, 'value_dest': 'message_text'},
            '1-0:31.7.0': {'value_parser': cls.__parse_float__, 'value_dest': 'instantaneous_current_l1'},
            '1-0:21.7.0': {'value_parser': cls.__parse_float__, 'value_dest': 'instantaneous_active_power_draw_l1'},
            '1-0:22.7.0': {'value_parser': cls.__parse_float__, 'value_dest': 'instantaneous_active_power_delivery_l1'},
            '0-1:24.1.0': {'value_parser': cls.__parse_int__, 'value_dest': 'num_mbus_devices'},
            '0-1:96.1.0': {'value_parser': cls.__parse_string__, 'value_dest': 'gas_meter_serial'},
            '0-1:24.2.1': {'value_parser': cls.__parse_float__, 'value_dest': 'gas_usage_total',
                           'meta_parser': cls.__timestamp__, 'meta_dest': 'gas_last_measurement'},
        }

        return field_mappings.get(fld, None)

    def __parse_record__(self, reading):
        pass
