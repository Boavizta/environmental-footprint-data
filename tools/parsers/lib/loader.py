"""Helper modules to load a parser easily."""
import io
import json
import sys
from typing import Callable, BinaryIO, Iterator

from tools.parsers.lib.data import DeviceCarbonFootprint


def main(parse_func: Callable[[BinaryIO, str], Iterator[DeviceCarbonFootprint]]) -> None:
    """Load a parser from the command line."""
    filename = sys.argv[1]
    with open(filename, 'rb') as file:
        body = io.BytesIO(file.read())
    for device in parse_func(body, filename):
        print(json.dumps(device.data, indent=2))
