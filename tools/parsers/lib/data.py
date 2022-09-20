import csv
import io
import hashlib
import math
import re
from sre_compile import isstring
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
    sources_hash: str
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
    gwp_transport_ratio: float
    gwp_eol_ratio: float
    gwp_ssd_ratio: float
    gwp_mainboard_ratio: float
    gwp_mainboard_ratio: float
    gwp_daughterboard_ratio: float
    gwp_enclosure_ratio: float
    

def md5_file(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def md5(pdf):
    hash_md5 = hashlib.md5()
    for chunk in iter(lambda: pdf.read(4096), b""):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()

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

def is_empty(x):
  return isinstance(x,str) and x=='' or not isinstance(x,str) and (math.isnan(x) or x==0)

def are_equal(a: Union[float, str, int], b: Union[float, str, int]):
    if isinstance(a, str) and isinstance(b, str):
        return a.strip()==b.strip()
    elif (not isinstance(a, str)) and (not isinstance(b, str)):
        return abs(a-b) <= 2e-3 * max(a,b)
    return False

def are_close_enough(a: Union[float, str, int], b: Union[float, str, int]):
    if isinstance(a, str) and isinstance(b, str):
        aval = re.sub(r'\s\s+', ' ', a.replace('”','in')).strip().lower()
        bval = re.sub(r'\s\s+', ' ', b.replace('”','in')).strip().lower()
        return aval==bval
    elif (not isinstance(a, str)) and (not isinstance(b, str)):
        # tolerate a 5% relative error
        return abs(a-b) <= 0.05 * max(a,b)
    return False

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
                raise ValueError(f'Value error for converting "{key}": "{value}" as"{data_type}"\n{data}') from error
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

    def reorder(self) -> 'DeviceCarbonFootprint':
        typed_data: DeviceCarbonFootprintData = {}
        for key in DeviceCarbonFootprintData.__annotations__.keys():
            if isstring(self.get(key)):
                typed_data[key]=self.get(key).replace(",","").replace("\"","").replace(";","").strip()
            else:
                typed_data[key]=self.get(key)
        return DeviceCarbonFootprint(typed_data)

    def as_csv_row(self, csv_format: Literal['us', 'fr'] = 'us') -> str:
        """Render the CSV row corresponding to this device model."""
        return _format_csv_row(
            [self.get(key)
             for key in DeviceCarbonFootprintData.__annotations__.keys()],
            csv_format=csv_format)

    @staticmethod
    def merge(device1: 'DeviceCarbonFootprint', device2: 'DeviceCarbonFootprint',
              conflict: Literal['keep2nd','interactive'] = 'keep2nd', verbose: bool = False) -> 'DeviceCarbonFootprint':
        """Merge two carbon footprints that are expected to correspond to the same device"""
        result: DeviceCarbonFootprintData = {}
        ignore_keys = ['added_date', 'add_method']
        conflicts = []
        for key in DeviceCarbonFootprintData.__annotations__.keys():
            v1 = device1.get(key)
            v2 = device2.get(key)
            if not is_empty(v1) and is_empty(v2):
                result[key]=v1
            elif is_empty(v1) and not is_empty(v2):
                result[key]=v2
            elif are_equal(v1,v2):
                result[key]=v2
            elif are_close_enough(v1,v2):
                if verbose:
                    print("WARNING, in merge,", key, ":", v1, "and", v2, "are considered close enough ->", v2)
                result[key]=v2
            elif key in ignore_keys:
                if verbose:
                    print("WARNING, in merge, ignore difference in field", key, ":", v1, "<->", v2)
                result[key]=v2
            elif key=='sources':
                if verbose:
                    print("WARNING, in merge source urls are different:")
                    print("  ignored: ", v1)
                    print("  retained:", v2)
                result[key]=v2
            else:
                conflicts.append(key)

        if len(conflicts)>0:
            k = 'n'
            if conflict=='interactive' or verbose:
                print("CONFLICT detected when merging", device1.get('manufacturer'), device1.get('name'), ":")
                for key in conflicts:
                    v1 = device1.get(key)
                    v2 = device2.get(key)
                    print(" | {0: >25} | {1: >30} -> {2: >30} |".format(key,v1,v2))
                if conflict=='interactive':
                    print("Press 'o' to keep the first column, or any other key to keep the second one...")
                    k = input()
            if k=='o':
                for key in conflicts:
                    result[key] = device1.get(key)
            else:
                for key in conflicts:
                    result[key] = device2.get(key)
        return DeviceCarbonFootprint(result)
