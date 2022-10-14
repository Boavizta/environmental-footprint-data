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
    re.compile(r'Product Environmental Report\s*(?P<name>.*)\sDate'),
    re.compile(r'(?P<screen_size>[0-9]+.?[0-9]{0,2})-inch'),
    re.compile(r'(?P<gwp_total>[0-9]+\.?[0-9]{0,2})\skg carbon emissions'),
    re.compile(r'(?P<gwp_manufacturing_ratio>[0-9]+\.?[0-9]{0,2})\%\s*Production'),
    re.compile(r'(?P<gwp_transport_ratio>[0-9]+\.?[0-9]{0,2})\%\s*Transport'),
    re.compile(r'(?P<gwp_use_ratio>[0-9]+\.?[0-9]{0,2})\%\s*Use'),
    re.compile(r'(?P<gwp_eol_ratio>[0-9]+\.?[0-9]{0,2})\%\s*End-of-life processing'),
    )

_CATEGORIES = {
    'iPhone': ('Workplace', 'Smartphone'),
    'iPad': ('Workplace', 'Tablet'),
    'MacBook': ('Workplace', 'Laptop'),
    'Watch': ('Home', 'IoT'),    
    'Display': ('Workplace', 'Monitor'),
    'HomePod': ('Home', 'IoT'),
    'TV': ('Home', 'EntertainmentT'),
    'iPod': ('Home', 'Entertainment'),
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
    if 'name' in extracted:
        result['name'] = extracted['name'].strip()
        for keyword, category_and_sub in _CATEGORIES.items():
            if keyword in result['name']:
                result['category'], result['subcategory'] = category_and_sub
                break
        result['name']=result['name'].replace("Apple ","")
    else:
        logging.error('The file "%s" did not match the HP pattern (no name extracted)', pdf_filename)
    if not "category" in result:
            result['category'] = "Datacenter"
    if 'gwp_total' in extracted:
        result['gwp_total'] = float(extracted['gwp_total'])
    if 'tolerance' in extracted and 'gwp_total' in result:
        result['gwp_error_ratio'] = round((float(extracted['tolerance']) / result['gwp_total']), 3)
    if 'date' in extracted:
        result['report_date'] = extracted['date']
    if 'weight' in extracted:
        result['weight'] = float(extracted['weight'].replace(' ',''))
    if 'screen_size' in extracted:
        result['screen_size'] = float(extracted['screen_size'])
    if 'cpu_quantity' in extracted:
        result['number_cpu'] = float(extracted['cpu_quantity'])
    if 'ram_capacity' in extracted:
        result['memory'] = float(extracted['ram_capacity'])
    if 'ssd_quantity' in extracted:
        result['hard_drive'] = extracted['ssd_quantity'] + " SSD"
    if 'assembly_location' in extracted:
        result['assembly_location'] = extracted['assembly_location']
    if 'lifetime' in extracted:
        result['lifetime'] = int(extracted['lifetime'])
    if 'use_location' in extracted:
        result['use_location'] = extracted['use_location']
    if 'energy_demand' in extracted:
        result['yearly_tec'] = float(extracted['energy_demand'].replace(' ',''))
    if 'gwp_manufacturing_ratio' in extracted:
        result['gwp_manufacturing_ratio'] = round(float(extracted['gwp_manufacturing_ratio'])/100,3)
    if 'gwp_use_ratio' in extracted:
        result['gwp_use_ratio'] = round(float(extracted['gwp_use_ratio'])/100,3)
    if 'gwp_eol_ratio' in extracted:
        result['gwp_eol_ratio'] = round(float(extracted['gwp_eol_ratio'])/100,3)
    else:
        if 'gwp_total' in result:
            if 'gwp_eol' in extracted:
                result['gwp_eol_ratio']=round(float(extracted['gwp_eol']) / result['gwp_total'],3) 
    if 'gwp_transport_ratio' in extracted:
        result['gwp_transport_ratio'] = float(extracted['gwp_transport_ratio'])/100 
    else:
        if 'gwp_total' in result:
            if 'gwp_transport' in extracted:
                result['gwp_transport_ratio']=round(float(extracted['gwp_transport']) / result['gwp_total'],3)
    if 'gwp_ssd_ratio' in extracted:
        result['gwp_ssd_ratio'] = float(extracted['gwp_ssd_ratio'])/100 
    else:
        if 'gwp_total' in result:
            if 'gwp_ssd' in extracted:
                result['gwp_ssd_ratio']=round(float(extracted['gwp_ssd']) / result['gwp_total'],3) 
    if 'gwp_mainboard_ratio' in extracted:
        result['gwp_mainboard_ratio'] = float(extracted['gwp_mainboard_ratio'])/100 
    else:
        if 'gwp_total' in result:
            if 'gwp_mainboard' in extracted:
                result['gwp_mainboard_ratio']=round(float(extracted['gwp_mainboard']) / result['gwp_total'],3)
    if 'gwp_daughterboard_ratio' in extracted:
        result['gwp_daughterboard_ratio'] = float(extracted['gwp_daughterboard_ratio'])/100 
    else:
        if 'gwp_total' in result:
            if 'gwp_daughterboard' in extracted:
                result['gwp_daughterboard_ratio']=round(float(extracted['gwp_daughterboard']) / result['gwp_total'],3)
    if 'gwp_enclosure_ratio' in extracted:
        result['gwp_enclosure_ratio'] = float(extracted['gwp_enclosure_ratio'])/100 
    else:
        if 'gwp_total' in result:
            if 'gwp_enclosure' in extracted:
                result['gwp_enclosure_ratio']=round(float(extracted['gwp_enclosure']) / result['gwp_total'],3)

    test = re.findall(r'(?P<storage>[0-9]+[A-Z]B)\s*(?P<impact>[0-9]+\.?[0-9]*)', pdf_as_text)
    result['comment']=""
    for i in test:
            result['comment']+= result['name'] + " " + i[0] + " (" + i[1] + "kgCO2eq), "
    now = datetime.datetime.now()
    result['added_date'] = now.strftime('%Y-%m-%d')
    result['add_method'] = "Apple Auto Parser"
    result['manufacturer'] = "Apple"
    yield data.DeviceCarbonFootprint(result)


# Convenient way to run this scraper as a standalone.
if __name__ == '__main__':
    loader.main(parse)
