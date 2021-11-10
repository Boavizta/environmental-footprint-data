"""Parsers for Huawei PDF.

See an example here https://download-c1.huawei.com/download/downloadCenter?downloadId=100485&version=435354&siteCode=worldwide
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
_HUAWEI_DESK_PATTERNS = (
    re.compile(r'Product:\s*(?P<name>\S.*?)\s*Product type:'),
    re.compile(r' Total greenhouse gas emissions.?: (?P<footprint>[0-9]+(?:.[0-9]+)?)\s*kg ?CO2 ?e'),
    re.compile(r'lifetime:\s*(?P<lifetime>[0-9]+) years'),
    re.compile(r' Weight:\s*(?P<weight>[0-9]*.[0-9]*)\s*grams'),
    re.compile(r' Screen:\s*(?P<screen_size>[0-9]*.[0-9]*)\s*-?inch'),
    re.compile(r' Final manufacturing location\s*(?P<assembly_location>[A-Za-z]*)\s+'),
    re.compile(r'^\s*(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})'),
)

_PRODUCT_PATTERN = re.compile(r'Product:\s*(?:Huawei\s*)?(\S.+\S)', re.I)
_PRODUCT_TYPE_PATTERN = re.compile(r'Product type:\s*(\S.+\S)', re.I)


def parse(body: BinaryIO, pdf_filename: str) -> Iterator[data.DeviceCarbonFootprint]:
    result = data.DeviceCarbonFootprintData()
    result['manufacturer'] = 'Huawei'

    # Parse text from PDF.
    pdf_as_text = pdf.pdf2txt(body)
    extracted = text.search_all_patterns(_HUAWEI_DESK_PATTERNS, pdf_as_text)
    if not extracted:
        logging.error('The file "%s" did not match the HP pattern', pdf_filename)
        return

    # Extract some text by line:
    if 'name' not in extracted:
        for rect, page in pdf.search_text(body, 'Product:'):
            line = page.get_textbox((rect.x0, rect.y0, rect.x1 * 5 - rect.x0 * 4, rect.y1))
            if (product_match := _PRODUCT_PATTERN.search(line)):
                extracted['name'] = product_match.group(1)
                break
    if 'type' not in extracted:
        for rect, page in pdf.search_text(body, 'Product type:'):
            line = page.get_textbox((rect.x0, rect.y0, rect.x1 * 5 - rect.x0 * 4, rect.y1))
            if (type_match := _PRODUCT_TYPE_PATTERN.search(line)):
                extracted['type'] = type_match.group(1)
                break

    # Convert each matched group to our format.
    if 'name' in extracted:
        result['name'] = extracted['name'].strip().removeprefix('Huawei ').removeprefix('HUAWEI ')
    if 'footprint' in extracted:
        result['gwp_total'] = float(extracted['footprint'])
    if 'date' in extracted:
        result['report_date'] = extracted['date']
    if 'weight' in extracted:
        result['weight'] = round(float(extracted['weight']) / 1000, 4)
    if 'screen_size' in extracted:
        result['screen_size'] = float(extracted['screen_size'])
    if 'lifetime' in extracted:
        result['lifetime'] = float(extracted['lifetime'])
    if 'type' in extracted:
        result['category'] = 'Workplace'
        result['subcategory'] = extracted['type'].replace('MediaPad', 'Tablet')
    now = datetime.datetime.now()
    result['added_date'] = now.strftime('%Y-%m-%d')
    result['add_method'] = "Huawei Auto Parser"

    # TODO(pascal): Explore images to pull out Use and Manufacturing percentages.

    yield data.DeviceCarbonFootprint(result)


# Convenient way to run this scraper as a standalone.
if __name__ == '__main__':
    loader.main(parse)
