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
            pass
