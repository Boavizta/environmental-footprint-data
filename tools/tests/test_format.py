"""Check that data files have the right format."""
import csv
import io
import os
import unittest

from tools.parsers.lib import data

_DATA_FOLDER = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
_DATA_FILE = os.path.join(_DATA_FOLDER, 'boavizta-data-us.csv')


class FormatsTest(unittest.TestCase):

    data_content: str

    @classmethod
    def setUpClass(cls) -> None:
        with open(_DATA_FILE, 'rt', encoding='utf-8') as data_file:
            cls.data_content = data_file.read()

    def test_trailing_endline(self) -> None:
        self.assertTrue(
            self.data_content.endswith('\n'), msg='Data file needs to end with a trailing newline')

    def test_read_format(self) -> None:
        reader = csv.DictReader(io.StringIO(self.data_content))
        for row in reader:
            data.DeviceCarbonFootprint.from_text(row)

    # TODO(pascal): Check that fr and us formats are in sync.


if __name__ == '__main__':
    unittest.main()
