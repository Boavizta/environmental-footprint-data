"""Run all tests for parsers.

This test uses the testdata folder:
 - any subfolder contains tests for the parser with the corresponding name
 - in each subfolder, each test file is located next to a _parsed.json file with the expectation.
"""
import io
import json
import os
from typing import Any
import unittest

from tools import parsers

_TESTDATA_FOLDER = os.path.join(os.path.dirname(__file__), 'testdata')


class ParsersTest(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.test_files = {
            parser_name: [
                filename
                for filename in os.listdir(os.path.join(_TESTDATA_FOLDER, parser_name))
                if not filename.endswith('_parsed.json')
            ]
            for parser_name in os.listdir(_TESTDATA_FOLDER)
        }

    def _load_expectation(self, parser_name: str, filename: str) -> Any:
        expectation_path = os.path.join(_TESTDATA_FOLDER, parser_name, f'{filename}_parsed.json')
        with open(expectation_path, 'rt', encoding='utf-8') as expectation_file:
            return json.load(expectation_file)

    def _assertDictAlmostEqual(self, a: Any, b: Any, delta: float = 1e-4) -> None:
        """Check equality of two dicts that might contain floats almost equal."""
        assert isinstance(a, dict)
        assert isinstance(b, dict)
        assert len(a) == len(b)
        assert set(a) == set(b)
        for key_a, value_a in a.items():
            value_b = b[key_a]
            if value_a == value_b:
                continue
            assert isinstance(value_a, (float, int))
            assert isinstance(value_b, (float, int))
            if a:
                assert abs(value_b / value_a - 1) < delta
            elif b:
                assert abs(value_a / value_b - 1) < delta

    def assertDictsAlmostEqual(self, a: Any, b: Any, delta: float = 1e-4) -> None:
        """Check equality of two dicts list that might contain floats almost equal."""
        try:
            assert isinstance(a, (list, tuple))
            assert isinstance(b, (list, tuple))
            assert len(a) == len(b)
            for index_a, value_a in enumerate(a):
                self._assertDictAlmostEqual(value_a, b[index_a], delta=delta)
            return
        except AssertionError:
            self.assertEqual(a, b)

    def test_parsers(self) -> None:
        self.maxDiff = None
        for parser_name, files in self.test_files.items():
            with self.subTest(parser=parser_name):
                self.assertTrue(hasattr(parsers, parser_name), msg='Missing parser')
                parser = getattr(parsers, parser_name)
                for filename in files:
                    with self.subTest(file=filename):
                        input_filename = os.path.join(_TESTDATA_FOLDER, parser_name, filename)
                        with open(input_filename, 'rb') as input_file:
                            input_body = io.BytesIO(input_file.read())
                        result = [device.data for device in parser(input_body, input_filename)]
                        for device_data in result:
                            device_data.pop('added_date', None)
                        expected = self._load_expectation(parser_name, filename)
                        self.assertDictsAlmostEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
