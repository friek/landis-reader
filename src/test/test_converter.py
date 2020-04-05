import os
from unittest import TestCase

from p1.converter import Converter


class TestConverter(TestCase):
    def test_convert_p1_message(self):
        with open(os.path.join(os.path.dirname(__file__), 'fixtures', 'reading-201912022211.txt')) as f:
            contents = f.read()
            converter = Converter()
            result = converter.convert_p1_message(contents)
            self.assertIsNotNone(result)

    def test_convert_to_json(self):
        with open(os.path.join(os.path.dirname(__file__), 'fixtures', 'reading-201912201650.txt')) as f:
            contents = f.read()
            converter = Converter()
            result = converter.convert_p1_message(contents)
            json = result.to_json()
            self.assertEqual('{"model": "XMX5LGBBFG1009315878", "output_version": "42", '
                             '"meter_time": "2019-12-20T16:51:07+01:00", '
                             '"serial": "4530303331303033323036313232303136", "total_usage_night": 7607.555, '
                             '"total_usage_day": 9683.121, "total_energy_delivered_day": 0.0, '
                             '"total_energy_delivered_night": 0.0, "active_tariff": 2, "current_power_usage": 0.674, '
                             '"current_power_delivery": 0.0, "num_power_interruptions": 2, '
                             '"num_long_power_interruptions": 0, "power_failure_event_log": "0", '
                             '"num_voltage_sags_phase_l1": 0, "num_voltage_swells_phase_l1": 0, "message_numeric": 0, '
                             '"message_text": null, "instantaneous_current_l1": 0.0, '
                             '"instantaneous_active_power_draw_l1": 0.674, '
                             '"instantaneous_active_power_delivery_l1": 0.0, "num_mbus_devices": 3, '
                             '"gas_meter_serial": "4730303435303031363036383036393136", '
                             '"gas_last_measurement": "2019-12-20T16:00:00+01:00", "gas_usage_total": 5080.562}', json)

    def test_convert_timezone(self):
        """
        This tests the proper format for the time. Python datetime doesn't appear to adhere to timezone
        offsets properly, so date conversion is now handled by the awesome pendulum module.
        :return:
        """
        with open(os.path.join(os.path.dirname(__file__), 'fixtures', 'reading-20200405093.txt')) as f:
            contents = f.read()
            converter = Converter()
            result = converter.convert_p1_message(contents)
            time = str(result.meter_time)
            self.assertEqual("2020-04-05T09:33:03+02:00", time)
