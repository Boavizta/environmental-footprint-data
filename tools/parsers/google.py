"""Parsers for Google Product sustainability PDF.

See an example here https://www.gstatic.com/gumdrop/sustainability/pixel5-product-environmental-report.pdf
"""
import logging
import re
import datetime
from typing import BinaryIO, Iterator

from tools.parsers.lib import data
from tools.parsers.lib import loader
from tools.parsers.lib import pdf
from tools.parsers.lib import text


# A list of patterns to search in the text.
_GOOGLE_PATTERNS = (
    re.compile(r'^(?P<name>.+?)Product environmental reportModel'),
    re.compile(r'Product environmental report(?P<name>.{,50})Model'),
    re.compile(r'over(?P<lifetime>[a-z]+)-year life cycle'),
    re.compile(r'assuming (?P<lifetime>[a-z]+) years of use'),
    re.compile(r'assuming a (?P<lifetime>[a-z]+)-year use period'),
    re.compile(r'assuming a (?P<lifetime>[a-z]+)-year life cycle'),
    re.compile(r'Total GHG emissions [^:]+:\s*(?P<footprint>[0-9]*)\s*kg ?CO2 ?e'),
    re.compile(r'year[s]? of use:[0-9]*\s*(?P<footprint>[0-9]*)\s*kg\s*CO2\s*e'),
    re.compile(r'life cycle:.\s*(?P<footprint>[0-9]*\.[0-9]*)\s*kg\s*CO2\s*e'),
    re.compile(r'Total materials:(?P<weight>[0-9]+)\s*g'),
    re.compile(r'Annual energy use estimate(?:[0-9]+ kWh(?:/y)?)\s*(?P<energy_demand>[0-9]+) kWh(?:/y)?'),
    re.compile(r'([0-9]*\.*[0-9]*)\s*kWh\s*Standby power'),
    re.compile(r' Screen size\s*(?P<screen_size>[0-9]*.[0-9]*)\s*inches'),
    re.compile(r' Final manufacturing location\s*(?P<assembly_location>[A-Za-z]*)\s+'),
    re.compile(r' introduced \s*(?P<date>[A-Z][a-z]+(?:\s+[0-9]?[0-9],)? [0-9]{4})')    
)

_USE_PERCENT_PATTERN = re.compile(r'.*Customer [u|U]se\s*([0-9]*\.*[0-9]*)\%.*')
_PRODUCTION_PERCENT_PATTERN = re.compile(r'.*Production\s*([0-9]*\.*[0-9]*)\%.*')
_EOL_PERCENT_PATTERN = re.compile(r'Recycling\s*([0-9]*\.*[0-9]*)%')
_TRANSPORT_PERCENT_PATTERN = re.compile(r'(Distribution|Transpor.*)\s*([0-9]*\.*[0-9]*)\s*%')

_ENGLISH_TO_NUMERIC = {
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'ten': 10,
}

_CATEGORIES = {
    'Pixelbook': ('Workplace', 'Laptop'),
    'Slate': ('Workplace', 'Tablet'),
    'Pixel': ('Workplace', 'Smartphone'),
    'Home': ('Home', 'IoT'),
    'Wifi': ('Home', 'Network'),
    'Stadia': ('Home', 'Gaming'),
    'Chromecast': ('Home', 'Multimedia'),
    'Daydream': ('Home', 'Multimedia'),
    'Nest': ('Home', 'IoT')
}


def parse(body: BinaryIO, pdf_filename: str) -> Iterator[data.DeviceCarbonFootprint]:
    result = data.DeviceCarbonFootprintData()
    result['manufacturer'] = 'Google'

    # Parse text from PDF.
    pdf_as_text = pdf.pdf2txt(body)
    extracted = text.search_all_patterns(_GOOGLE_PATTERNS, pdf_as_text)
    if not extracted:
        logging.error('The file "%s" did not match the Google pattern', pdf_filename)
        return

    # Convert each matched group to our format.
    if 'name' in extracted:
        result['name'] = extracted['name'].strip().removeprefix('Google ')
    else:
        # Search name again but in the first page only.
        first_page_text = pdf.pdf2txt(body, num_pages=1)
        result['name'] = first_page_text\
            .replace('Product environmental report', '').strip()\
            .removeprefix('Google ')
    for keyword, category_and_sub in _CATEGORIES.items():
        if keyword in result['name']:
            result['category'], result['subcategory'] = category_and_sub
            break
    if 'footprint' in extracted:
        result['gwp_total'] = float(extracted['footprint'])
    if 'date' in extracted:
        result['report_date'] = extracted['date']
    if 'weight' in extracted:
        result['weight'] = float(extracted['weight']) / 1000
    if 'lifetime' in extracted:
        lifetime = extracted['lifetime']
        if numeric_lifetime := _ENGLISH_TO_NUMERIC.get(lifetime):
            result['lifetime'] = numeric_lifetime
        else:
            raise ValueError(f'Could not convert "{lifetime}" to a numeric value')
    if 'energy_demand' in extracted:
        result['yearly_tec'] = float(extracted['energy_demand'])

    now = datetime.datetime.now()
    result['added_date'] = now.strftime('%Y-%m-%d')
    result['add_method'] = "Google Auto Parser"

    for block, page in pdf.search_text(body, 'Customer use'):
        # Look for percentage below "Customer use".
        use_text = page.get_textbox((block.x0, block.y0, block.x1, block.y1 * 2.1 - block.y0))
        if (use_match := _USE_PERCENT_PATTERN.search(use_text)):
            result['gwp_use_ratio'] = round(float(use_match.group(1)) / 100,3)
            break
    for block, page in pdf.search_text(body, 'Production'):
        # Look for percentage below "Production".
        prod_text = page.get_textbox((block.x0, block.y0, block.x1, block.y1 * 2.1 - block.y0))
        if (prod_match := _PRODUCTION_PERCENT_PATTERN.search(prod_text)):
            result['gwp_manufacturing_ratio'] = round(float(prod_match.group(1)) / 100,3)
            break
    for block, page in pdf.search_text(body, 'Recycling'):
        # Look for percentage below "EoL".
        eol_text = page.get_textbox((block.x0, block.y0, block.x1, block.y1 * 2.1 - block.y0))
        if (eol_match := _EOL_PERCENT_PATTERN.search(eol_text)):
            result['gwp_eol_ratio'] = round(float(eol_match.group(1)) / 100,3)
            break
    for block, page in pdf.search_text(body, 'Distribution'):
        # Look for percentage below "Transport".
        transport_text = page.get_textbox((block.x0, block.y0, block.x1, block.y1 * 2.1 - block.y0))
        if (transport_match := _TRANSPORT_PERCENT_PATTERN.search(transport_text)):
            result['gwp_transport_ratio'] = round(float(transport_match.group(2)) / 100,3)
            break
    for block, page in pdf.search_text(body, 'Transportation'):
        # Look for percentage below "Transport".
        transport_text = page.get_textbox((block.x0, block.y0, block.x1, block.y1 * 2.1 - block.y0))
        if (transport_match := _TRANSPORT_PERCENT_PATTERN.search(transport_text)):
            result['gwp_transport_ratio'] = round(float(transport_match.group(2)) / 100,3)
            break

    yield data.DeviceCarbonFootprint(result)


# Convenient way to run this scraper as a standalone.
if __name__ == '__main__':
    loader.main(parse)
