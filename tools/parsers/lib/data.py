import csv
import io
from typing import Any, Dict, Iterable, Iterator, Literal, Union, TextIO, TypedDict


class DeviceCarbonFootprintData(TypedDict, total=False):
    """The carbon footprint data for one device model."""
    manufacturer: str
    name: str
    category: str
    subcategory: str
    gwp_total: float
    gwp_use_ratio: float
    yearly_tec: float
    lifetime: float
    use_location: str
    report_date: str
    sources: str
    gwp_error_ratio: float
    gwp_manufacturing_ratio: float
    weight: float
    assembly_location: str
    screen_size: float
    server_type: str
    hard_drive: str
    memory: float
    number_cpu: int
    height: int
    added_date: str
    add_method: str


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
            if not (value := data.get(key)):
                continue
            try:
                typed_data[key] = data_type(value)  # type: ignore
            except ValueError as error:
                raise ValueError(f'Value error for "{key}": "{value}"\n{data}') from error
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
