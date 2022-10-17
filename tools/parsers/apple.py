"""Parsers for Apple PDF.

See an example here https://www.hpe.com/psnow/doc/a50002756enw?jumpid=in_hpesitesearch
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
_APPLE_PATTERNS = (
    re.compile(r'(?P<name>.*)\s*Environmental\s*Report\s*Apple'),
    re.compile(r'Product Environmental Report\s*(?P<name>.*)\s*Date'),
    re.compile(r'Date\s*introduced\s*(?P<date>[A-Z][a-z]*\s*[0-9]*\,\s*[0-9]{4})'),
    re.compile(r'(?P<screen_size>[0-9]+.?[0-9]{0,2})-inch'),
    re.compile(r'(?P<gwp_total>[0-9]*)\s*kg\s*CO2e\s*Total'),
    re.compile(r'life cycle\s*(?P<gwp_total>[0-9]*)\s*kg'),
    re.compile(r'assumes\s*a\s*(?P<lifetime>.*)-year period'),
    re.compile(r'Product Environmental Report\s*(?P<name>.*)\sDate'),
    re.compile(r'standards\s*and\s*based\s*on\s*(?P<longname>[^.]*)\.'),
    re.compile(r'(?P<screen_size>[0-9]+.?[0-9]{0,2})-inch'),
    re.compile(r'(?P<gwp_total>[0-9]+\.?[0-9]{0,2})\skg carbon emissions'),
    re.compile(r'(?P<gwp_manufacturing_ratio>[0-9]+\.?[0-9]{0,2})\%[^a-zA-Z0-9]*Production'),
    re.compile(r'(?P<gwp_transport_ratio>[0-9]+\.?[0-9]{0,2})\%[^a-zA-Z0-9]*Transport'),
    re.compile(r'(?P<gwp_use_ratio>[0-9]+\.?[0-9]{0,2})\%[^a-zA-Z0-9]*(Use|Customer use)'),
    re.compile(r'(?P<gwp_eol_ratio>[0-9]+\.?[0-9]{0,2})\%[^a-zA-Z0-9]*(End-of-life processing|Recycling)'),
)

_ENGLISH_TO_NUMERIC = {
    'one': 1,
    'two': 2,
    'three': 3,
    'three- or four': 3.5,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'ten': 10,
}

_CATEGORIES = {
    'iPhone': ('Workplace', 'Smartphone'),
    'iPad': ('Workplace', 'Tablet'),
    'MacBook': ('Workplace', 'Laptop'),
    'Watch': ('Home', 'IoT'),    
    'Display': ('Workplace', 'Monitor'),
    'HomePod': ('Home', 'IoT'),
    'TV': ('Home', 'EntertainmentT'),
    'iPod': ('Home', 'Entertainment'),
    'Mac ': ('Workplace', 'Desktop'),
    'iMac': ('Workplace', 'Desktop'),
}

def parse(body: BinaryIO, pdf_filename: str) -> Iterator[data.DeviceCarbonFootprint]:
    result = data.DeviceCarbonFootprintData()


    # Parse text from PDF.
    pdf_as_text = pdf.pdf2txt(body)
    extracted = text.search_all_patterns(_APPLE_PATTERNS, pdf_as_text)
    if not extracted:
        logging.error('The file "%s" did not match the Apple pattern', pdf_filename)
        return

    # Convert each matched group to our format.
    if 'longname' in extracted:
        result['name'] = extracted['longname'].strip()
        storage=re.search(r'([0-9]*)(GB|TB)',result['name'])
        if storage:
            result['hard_drive'] = storage[0] + " SSD"
        for keyword, category_and_sub in _CATEGORIES.items():
            if keyword in result['name']:
                result['category'], result['subcategory'] = category_and_sub
                break
    else:
        if 'name' in extracted:
            result['name'] = extracted['name'].strip()
            for keyword, category_and_sub in _CATEGORIES.items():
                if keyword in result['name']:
                    result['category'], result['subcategory'] = category_and_sub
                    break
            result['name']=result['name'].replace("Apple ","")
        else:
            logging.error('The file "%s" did not match the HP pattern (no name extracted)', pdf_filename)
    result['name']=result['name'].replace(" storage","")
    result['name']=result['name'].replace(" configuration","")
    result['name']=result['name'].replace(" standard","")
    if not "category" in result:
            result['category'] = "Workplace"
    if 'gwp_total' in extracted:
        result['gwp_total'] = float(extracted['gwp_total'])
    if 'date' in extracted:
        result['report_date'] = extracted['date']
    if 'screen_size' in extracted:
        result['screen_size'] = float(extracted['screen_size'])
    if 'assembly_location' in extracted:
        result['assembly_location'] = extracted['assembly_location']
    if 'lifetime' in extracted:
        lifetime = extracted['lifetime']
        if numeric_lifetime := _ENGLISH_TO_NUMERIC.get(lifetime):
            result['lifetime'] = numeric_lifetime
        else:
            raise ValueError(f'Could not convert "{lifetime}" to a numeric value')
    result['use_location'] = "WW"
    if 'gwp_manufacturing_ratio' in extracted:
        result['gwp_manufacturing_ratio'] = round(float(extracted['gwp_manufacturing_ratio'])/100,3)
    if 'gwp_use_ratio' in extracted:
        result['gwp_use_ratio'] = round(float(extracted['gwp_use_ratio'])/100,3)
    if 'gwp_eol_ratio' in extracted:
        result['gwp_eol_ratio'] = round(float(extracted['gwp_eol_ratio'])/100,3)
    if 'gwp_transport_ratio' in extracted:
        result['gwp_transport_ratio'] = float(extracted['gwp_transport_ratio'])/100 
    test = re.findall(r'(?P<storage>[0-9]+[A-Z]B)\s*(?P<impact>[0-9]+\.?[0-9]*)', pdf_as_text)
    result['comment']=""
    for i in test:
            result['comment']+= extracted['name'] + " " + i[0] + " (" + i[1] + "kgCO2eq) - "
    now = datetime.datetime.now()
    result['added_date'] = now.strftime('%Y-%m-%d')
    result['add_method'] = "Apple Auto Parser"
    result['manufacturer'] = "Apple"
    yield data.DeviceCarbonFootprint(result)


# Convenient way to run this scraper as a standalone.
if __name__ == '__main__':
    loader.main(parse)
