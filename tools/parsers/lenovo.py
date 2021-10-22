"""Parsers for Lenovo LCA PDF.

See an example here https://static.lenovo.com/ww/docs/regulatory/eco-declaration/pcf-lenovo-e41-45.pdf
"""

import logging
import re
import datetime
from typing import BinaryIO, Iterator

from .lib import data
from .lib import loader
from .lib import pdf
from .lib import text


# A list of patterns to search in the text.
_LENOVO_LCA_PATTERNS = (
    re.compile(r'Commercial Name (?P<name>.*?)\s*Model'),
    re.compile(r' Issue Date\s*(?P<date>[A-Z][a-z][0-9]*, [0-9]{4})'),
    re.compile(
        r' report this value as\s*(?P<footprint>[0-9]+)\s*'
        r'\+/-\s*(?P<error>[0-9]+) kg of CO2e'),
    re.compile(r' Product Weight\s*kg\s*(Input\s*)?(?P<weight>[0-9]*.[0-9]*)'),
    re.compile(r' Screen Size\s*inches\s*(?P<screen_size>[0-9]+\.[0-9]+)'),
    re.compile(r'Assembly Location\s*no unit\s*(?P<assembly_location>[A-Za-z]*)\s+'),
    re.compile(r'Product Lifetime\s*years\s*(Input\s*)?(?P<lifetime>[0-9]*)'),
    re.compile(r' Use Location\s*no unit\s*(?P<use_location>[A-Za-z]*)\s+'),
)

_USE_PERCENT_PATTERN = re.compile(r'.*Use([0-9]*\.*[0-9]*)\%.*')


def parse(body: BinaryIO, pdf_filename: str) -> Iterator[data.DeviceCarbonFootprint]:
    result = data.DeviceCarbonFootprintData()
    result['Manufacturer'] = 'Lenovo'

    # Parse text from PDF.
    pdf_as_text = pdf.pdf2txt(body)
    extracted = text.search_all_patterns(_LENOVO_LCA_PATTERNS, pdf_as_text)
    if not extracted:
        logging.error('The file "%s" did not match the Lenovo pattern', pdf_filename)
        return

    # Convert each matched group to our format.
    if 'name' in extracted:
        result['Name'] = extracted['name'].strip().removeprefix('Lenovo ')
    if 'footprint' in extracted:
        result['Total (kgCO2eq)'] = float(extracted['footprint'])
    if result.get('Total (kgCO2eq)') and 'error' in extracted:
        result['Error (%)'] = round((float(extracted['error']) / result['Total (kgCO2eq)']), 4)
    else:
        raise ValueError((repr(pdf_as_text), extracted))
    if 'date' in extracted:
        result['Date'] = extracted['date']
    if 'weight' in extracted:
        result['Weight'] = float(extracted['weight'])
    if 'screen_size' in extracted:
        result['Screen size'] = float(extracted['screen_size'])
    if 'assembly_location' in extracted:
        result['Assembly Location'] = extracted['assembly_location']
    if 'lifetime' in extracted:
        result['Lifetime'] = float(extracted['lifetime'])
    if 'use_location' in extracted:
        result['Use Location'] = extracted['use_location']
    if 'energy_demand' in extracted:
        result['Yearly TEC (kWh)'] = float(extracted['energy_demand'])
    if 'hdd' in extracted:
        result['HD/SSD'] = extracted['hdd']
    if 'ram' in extracted:
        result['RAM'] = float(extracted['ram'])
    if 'cpu' in extracted:
        result['CPU'] = int(extracted['cpu'])
    now = datetime.datetime.now()
    result['Added Date'] = now.strftime('%Y-%m-%d')
    result['Add Method'] = "Lenovo Auto Parser"

    # TODO(pascal): Explore images to pull out Use and Manufacturing percentages.

    yield data.DeviceCarbonFootprint(result)


# Convenient way to run this scraper as a standalone.
if __name__ == '__main__':
    loader.main(parse)
