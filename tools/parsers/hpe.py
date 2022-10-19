"""Parsers for HPE PDF.

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
_HPE_PATTERNS = (
    re.compile(r'HPE\s*PRODUCT\s*CARBON\s*FOOTPRINT\s*(?P<name>.*?)\s*At HPE'),
    re.compile(r'QuickSpecs:\s*(?P<name>.*?)\s*The inputs'), 
    re.compile(r'ESTIMATED PRODUCT CARBON FOOTPRINT\:\*?\s*(?P<footprint>[0-9]*)\s*kg\s*CO2\s*e'),
    re.compile(r'The mean carbon footprint for this product is\s*(?P<footprint>[0-9]*)\s*kg\s*CO2\s*e'),
    re.compile(r'with a standard deviation of\s*(?P<tolerance>[0-9]*)\skg\s*CO2\s*e'),
    re.compile(r'Product lifetime\s*(?P<lifetime>[0-9]*)\s*years'),
    re.compile(r'Use location\s*(?P<use_location>(EU|US|Europe|North America|China|WW|Worldwide))'),
    re.compile(r'nergy demand \((Y|y)early TEC\)\s*(?P<energy_demand>[0-9]*\.[0-9]*)\s*kWh'),
    re.compile(r'Product weight\s*(?P<weight>[0-9]*\.?\s*[0-9]*)\s*kg'),
    re.compile(r'CPU quantity \(mainboard\)\s*(?P<cpu_quantity>[0-9]*)\s*'),
    re.compile(r'DRAM capacity \(mainboard\)\s*(?P<ram_capacity>[0-9]*)\s*GB'),
    re.compile(r'SSD quantity \(storage\)\s*(?P<ssd_quantity>[0-9]*)\s*'),
    re.compile(r'Server type\s*(?P<server_type>(Tower|Rack))\s*'),
    re.compile(r'(?P<server_size>[1-6])U\s*server'),
    re.compile(r'Assembly location\s*(?P<assembly_location>(EU|US|Europe|North America|China|WW|Worldwide))'),
    re.compile(r'Copyright \s*(?P<date>[0-9]{4}) '),
    re.compile(r'Use\s*\((?P<gwp_use_ratio>[0-9]*\.?[0-9]*)%\)'),
    re.compile(r'Supply chain\s*\((?P<gwp_manufacturing_ratio>[0-9]*\.?[0-9]*)%\)'),
    re.compile(r'End (O|o)f (L|l)ife\s*(?P<gwp_eol>[0-9]*\.?[0-9]*)\s*kg\s*CO2'),
    re.compile(r'Transport\s*(?P<gwp_transport>[0-9]*\.?[0-9]*)\s*kg\s*CO2'),
    re.compile(r'Mainboard\s*(?P<gwp_mainboard>[0-9]*\.?[0-9]*)\s*kg\s*CO2'),
    re.compile(r'SSD\s*(?P<gwp_ssd>[0-9]*\.?[0-9]*)\s*kg\s*CO2'),
    re.compile(r'Daughterboard[^0-9]*(?P<gwp_daughterboard>[0-9]*\.?[0-9]*)\s*kg\s*CO2'),
    re.compile(r'(Enclosure|PSU)[^0-9]*(?P<gwp_enclosure>[0-9]*\.?[0-9]*)\s*kg\s*CO2'),
    re.compile(r'Assembly[^0-9]*(?P<gwp_assembly>[0-9]*\.?[0-9]*)\s*kg\s*CO2'),
)

_CATEGORIES = {
    'Proliant': ('Datacenter', 'Server'),
    'Edgeline': ('Datacenter', 'Converged Edge'),
    'Synergy': ('Datacenter', 'Converged'),
}

def parse(body: BinaryIO, pdf_filename: str) -> Iterator[data.DeviceCarbonFootprint]:
    result = data.DeviceCarbonFootprintData()


    # Parse text from PDF.
    pdf_as_text = pdf.pdf2txt(body)
    #print(pdf_as_text)
    extracted = text.search_all_patterns(_HPE_PATTERNS, pdf_as_text)
    if not extracted:
        logging.error('The file "%s" did not match the HPE pattern', pdf_filename)
        return

    # Convert each matched group to our format.
    if 'name' in extracted:
        result['name'] = extracted['name'].strip()
        for keyword, category_and_sub in _CATEGORIES.items():
            if keyword in result['name']:
                result['category'], result['subcategory'] = category_and_sub
                break
        result['name']=result['name'].replace("HPE ","")
    else:
        logging.error('The file "%s" did not match the HP pattern (no name extracted)', pdf_filename)
    if not "category" in result:
            result['category'] = "Datacenter"
    if 'footprint' in extracted:
        result['gwp_total'] = float(extracted['footprint'])
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
    #test CI
    now = datetime.datetime.now()
    result['added_date'] = now.strftime('%Y-%m-%d')
    result['add_method'] = "HPE Auto Parser"
    result['manufacturer'] = "HPE"
    yield data.DeviceCarbonFootprint(result)


# Convenient way to run this scraper as a standalone.
if __name__ == '__main__':
    loader.main(parse)