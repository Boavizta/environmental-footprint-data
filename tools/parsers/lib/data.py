import csv
import io
from typing import Any, Dict, Iterable, Iterator, Literal, Union, TextIO, TypedDict

# The carbon footprint data for one device model.
DeviceCarbonFootprintData = TypedDict('DeviceCarbonFootprintData', {
    'Manufacturer': str,
    'Name': str,
    'Category': str,
    'Subcategory': str,
    'Total (kgCO2eq)': float,
    'Use (%)': float,
    'Yearly TEC (kWh)': float,
    'Lifetime': float,
    'Use Location': str,
    'Date': str,
    'Sources': str,
    'Error (%)': float,
    'Manufacturing': float,
    'Weight': float,
    'Assembly Location': str,
    'Screen size': float,
    'Server Type': str,
    'HD/SSD': str,
    'RAM': float,
    'CPU': int,
    'U': int,
    'Added Date': str,
    'Add Method': str
}, total=False)


def _format_csv_row(row: Iterable[Any], csv_format: Literal['us', 'fr']) -> str:
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';' if csv_format == 'fr' else ',')
    writer.writerow([
        str(value).replace('.', ',')
        if csv_format == 'fr' and isinstance(value, float)
        else str(value)
        for value in row
    ])
    return output.getvalue()


class DeviceCarbonFootprint:
    """A class to manipulate device carbon footprint."""

    def __init__(self, data: DeviceCarbonFootprintData):
        self.data = data

    def __str__(self) -> str:
        return str(self.data)

    def __repr__(self) -> str:
        return f'DeviceCarbonFootprint({self.data})'

    @classmethod
    def from_text(cls, data: Dict[str, str]) -> 'DeviceCarbonFootprint':
        typed_data: DeviceCarbonFootprintData = {}
        for key, data_type in DeviceCarbonFootprintData.__annotations__.items():
            if not data.get(key):
                continue
            value = data[key]
            typed_data[key] = data_type(value)  # type: ignore
        return DeviceCarbonFootprint(typed_data)

    def get(self, key: str) -> Union[float, str, int]:
        if key in self.data:
            return self.data[key]  # type: ignore
        if key not in DeviceCarbonFootprintData.__annotations__:
            raise ValueError(f'DeviceCarbonFootprint has no such field "{key}')
        return ''

    @staticmethod
    def csv_headers(csv_format: Literal['us', 'fr'] = 'us') -> str:
        """Headers to build a CSV with data."""
        return _format_csv_row(
            DeviceCarbonFootprintData.__annotations__.keys(), csv_format=csv_format)

    def as_csv_row(self, csv_format: Literal['us', 'fr'] = 'us') -> str:
        """Render the CSV row corresponding to this device model."""
        return _format_csv_row(
            [self.get(key)
             for key in DeviceCarbonFootprintData.__annotations__.keys()],
            csv_format=csv_format)
