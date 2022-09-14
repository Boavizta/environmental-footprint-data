"""Parsers for Microsoft Product sustainability PDF.
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
_MS_PATTERNS = (
    re.compile(r'(Ecoprofile)|(ECOPROFILE)\s*(?P<name>.{5,30})\s*Our commitment'),
    re.compile(r'(?P<lifetime>[a-z]+) years of product use'),
    re.compile(r'Global warming potential\s*(?P<footprint>[0-9]*.[0-9]*)\s*kg\s*CO2.equivalent'),
    re.compile(r'Greenhouse gas emissions\s*(?P<footprint>[0-9]*.[0-9]*)\s*kg\s*CO2.equivalent'),
    re.compile(r'(?P<energy_demand>[0-9]*.[0-9]*)\s*kW[h]*\s*ENERGY STAR'),
    re.compile(r'([0-9]*\.*[0-9]*)\s*kWh\s*Standby power'),
    re.compile(r' Screen size\s*(?P<screen_size>[0-9]*.[0-9]*)\s*inches'),
    re.compile(r' Final manufacturing location\s*(?P<assembly_location>[A-Za-z]*)\s+'),
    re.compile(r'(?P<date>[A-Z][a-z]+(?:\s+[0-9]?[0-9],)? [0-9]{4})\s*©\s*[0-9]{4}\s*Microsoft\s*Corporatio'),
    re.compile(r'Product use\s*\((?P<gwp_use>[0-9]*\.*[0-9]*)\skg\sCO2eq\)'),
    re.compile(r'Manufacturing\s*\(\<?(?P<gwp_manuf>[0-9]*\.*[0-9]*)\skg\sCO2eq\)'),
    re.compile(r'Transport\s*\(\<?(?P<gwp_transport>[0-9]*\.*[0-9]*)\skg\sCO2eq\)'),
    re.compile(r'Disposal\s*\(\<?(?P<gwp_eol>[0-9]*\.*[0-9]*)\skg\sCO2eq\)'),
    re.compile(r'End of life\s*\(\<?(?P<gwp_eol>[0-9]*\.*[0-9]*)\skg\sCO2eq\)')
)

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
    'Surface': ('Workplace', 'Tablet'),
    'Xbox': ('Home', 'Gaming')
}

_DATE_PATTERN = re.compile(r'([A-Z][a-z]+(?:\s+[0-9]?[0-9],)? [0-9]{4})\s*©\s*[0-9]{4}\s*Microsoft\s*Corporatio')
_WEIGHT_PATTERN = re.compile(r'DEVICE\s*Weight.?\s*([0-9]*)\s*g')

def parse(body: BinaryIO, pdf_filename: str) -> Iterator[data.DeviceCarbonFootprint]:
    result = data.DeviceCarbonFootprintData()
    result['manufacturer'] = 'Microsoft'

    # Parse text from PDF.
    pdf_as_text = pdf.pdf2txt(body)
    extracted = text.search_all_patterns(_MS_PATTERNS, pdf_as_text)
    if not extracted:
        logging.error('The file "%s" did not match the Miccosoft pattern', pdf_filename)
        return

    # Convert each matched group to our format.
    if 'name' in extracted:
        result['name'] = extracted['name'].strip()
    else:
        first_page_text = pdf.pdf2txt(body, num_pages=1)
        result['name'] = first_page_text\
            .replace('ECOPROFILE', '').strip()
    for keyword, category_and_sub in _CATEGORIES.items():
        if keyword in result['name']:
            result['category'], result['subcategory'] = category_and_sub
            break
    if 'footprint' in extracted:
        result['gwp_total'] = float(extracted['footprint'])
    if 'date' in extracted:
        result['report_date'] = extracted['date']
    else:
        for block, page in pdf.search_text(body, 'Microsoft Corporation. All rights reserved'):
            date_text = page.get_textbox((block.x0 - 30, block.y0 - 10, block.x1, block.y1 * 2.1 - block.y0))
            if (date_match := _DATE_PATTERN.search(date_text)):
                result['report_date'] = date_match.group(1)
                break
    for block, page in pdf.search_text(body, 'Physical features'):
        weight_text = page.get_textbox((block.x0, block.y0, block.x1 + 10, block.y1 - 30 ))
        if (weight_match := _WEIGHT_PATTERN.search(weight_text)):
            result['weight'] = int(weight_match.group(1)) / 1000
            break
    if 'lifetime' in extracted:
        lifetime = extracted['lifetime']
        if numeric_lifetime := _ENGLISH_TO_NUMERIC.get(lifetime):
            result['lifetime'] = numeric_lifetime
        else:
            raise ValueError(f'Could not convert "{lifetime}" to a numeric value')
    if 'energy_demand' in extracted:
        result['yearly_tec'] = float(extracted['energy_demand'])
    if 'gwp_total' in result:
        if 'gwp_use' in extracted:
            result['gwp_use_ratio']=round(float(extracted['gwp_use']) / result['gwp_total'],3)
        if 'gwp_eol' in extracted:
            result['gwp_eol_ratio']=round(float(extracted['gwp_eol']) / result['gwp_total'],3)
        if 'gwp_transport' in extracted:
            result['gwp_transport_ratio']=round(float(extracted['gwp_transport']) / result['gwp_total'],3)
        if 'gwp_manuf' in extracted:
            result['gwp_manufacturing_ratio']=round(float(extracted['gwp_manuf']) / result['gwp_total'],3)
    now = datetime.datetime.now()
    result['added_date'] = now.strftime('%Y-%m-%d')
    result['add_method'] = "Microsoft Auto Parser"

    yield data.DeviceCarbonFootprint(result)


# Convenient way to run this scraper as a standalone.
if __name__ == '__main__':
    loader.main(parse)
