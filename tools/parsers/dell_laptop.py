"""Parsers for Dell LCA PDF.

See an example here https://i.dell.com/sites/csdocuments/CorpComm_Docs/en/carbon-footprint-wyse-3030.pdf
"""
import logging
import re
import datetime
from typing import BinaryIO, Iterator, Dict, Any

from tools.parsers.lib import data
from tools.parsers.lib.image import crop, find_text_in_image, image_to_text
from tools.parsers.lib import loader
from tools.parsers.lib import pdf
from tools.parsers.lib import text
from matplotlib import pyplot as plt
from tools.parsers.lib import piechart_analyser


# A list of patterns to search in the text.
_DELL_LCA_PATTERNS = (
    re.compile(r'(?P<name>[^\s]{3}.*?)(?: \))?\s*From design to end-of-life'),
    re.compile(r' page 1 (?P<name>.*?)\s*From design to end-of-life'),
    re.compile(r'(?P<name>VxRail.*?)\s*Report'),
    re.compile(r' estimated carbon footprint\: \s*(?P<footprint>[0-9]*) kgCO2e(?: \+\/\- (?P<error>[0-9]*)\s*kgCO2e)?'),
    re.compile(r' estimated ?standard deviation (of )?\+\/\- (?P<error>[0-9]*)\s*kgCO2e'),
    re.compile(r'mean of (?P<footprint>[0-9]+)\s*kg'),
    re.compile(r'standard deviation of (?P<error>[0-9]+)\s*kg'),
    re.compile(r' Report produced\s*(?P<date>[A-Z][a-z]*,* [0-9]{4}) '),
    re.compile(r' Product Weight\s*(?P<weight>[0-9]*.[0-9]*)\s*kg'),
    re.compile(r' Screen Size\s*(?P<screen_size>[0-9]+\.?[0-9]*)'),
    re.compile(r'Assembly Location\s*(?P<assembly_location>[A-Za-z]*)\s+'),
    re.compile(r'Product Lifetime\s*(?P<lifetime>[0-9]*) years'),
    re.compile(r' Use Location\s*(?P<use_location>[A-Za-z]*)\s+'),
    re.compile(r' Energy Demand \(Yearly TEC\)\s*(?P<energy_demand>[0-9]*.[0-9]*)\s*kWh'),
    re.compile(r' HDD\/SSD Quantity (?P<hdd>.*(?:SSD|HDD?))\s+'),
    re.compile(r' HDD\/SSD Quantity (?P<hdd>.*)\sDRAM'),
    re.compile(r' DRAM Capacity\s*(?P<ram>[0-9]*)\s*[A-Z]{2}\s+'),
    re.compile(r' CPU Quantity\s*(?P<cpu>[0-9]*)\s+'),
    re.compile(r'Use\s*(?P<gwp_use_ratio>[0-9]*\.*[0-9]*)%'),
    re.compile(r'Manufacturing\s*(?P<gwp_manufacturing_ratio>[0-9]*\.*[0-9]*)%'),
    re.compile(r'EoL\s*(?P<gwp_eol_ratio>[0-9]*\.*[0-9]*)%'),
    re.compile(r'Transportation\s*(?P<gwp_transport_ratio>[0-9]*\.*[0-9]*)%')
)

_USE_PERCENT_PATTERN = re.compile(r'.*Use([0-9]*\.*[0-9]*)\%.*')
_MANUF_PERCENT_PATTERN = re.compile(r'.*nufac[a-z0-9]*[a-z][^0-9\.]([0-9]*\.*[0-9]*)\%.*')
_EOL_PERCENT_PATTERN = re.compile(r'.*EoL([0-9]*\.*[0-9]*)\%.*')
_TRANSPORT_PERCENT_PATTERN = re.compile(r'.*port[A-Za-z]*[^0-9\.]?([0-9]*\.*[0-9]*)\%.*')


def parse(body: BinaryIO, pdf_filename: str) -> Iterator[data.DeviceCarbonFootprint]:
    result = data.DeviceCarbonFootprintData()
    
    # Parse text from PDF.
    pdf_as_text = pdf.pdf2txt(body)
    extracted = text.search_all_patterns(_DELL_LCA_PATTERNS, pdf_as_text)
    if not extracted:
        logging.error('The file "%s" did not match the Dell pattern', pdf_filename)
        return

    # Convert each matched group to our format.
    if 'name' in extracted:
        result['name'] = extracted['name'].strip().removeprefix('Dell ')
    else:
        raise ValueError(pdf_as_text)
    if 'footprint' in extracted:
        result['gwp_total'] = float(extracted['footprint'])
    else:
        raise ValueError(pdf_as_text)
    if result.get('gwp_total') and 'error' in extracted:
        result['gwp_error_ratio'] = round((float(extracted['error']) / result['gwp_total']), 3)
    elif not "GaBi" in pdf_as_text:
        raise ValueError(pdf_as_text)
    if 'date' in extracted:
        result['report_date'] = extracted['date']
    if 'weight' in extracted:
        result['weight'] = float(extracted['weight'])
    if 'screen_size' in extracted:
        result['screen_size'] = float(extracted['screen_size'])
    else:
        result['screen_size'] = 0
    if 'assembly_location' in extracted:
        result['assembly_location'] = extracted['assembly_location']
    if 'lifetime' in extracted:
        result['lifetime'] = float(extracted['lifetime'])
    if 'use_location' in extracted:
        result['use_location'] = extracted['use_location']
    if 'energy_demand' in extracted:
        result['yearly_tec'] = float(extracted['energy_demand'])
    if 'hdd' in extracted:
        result['hard_drive'] = extracted['hdd'].replace('BG','GB')
    if 'ram' in extracted:
        result['memory'] = float(extracted['ram'])
    if 'cpu' in extracted:
        result['number_cpu'] = int(extracted['cpu'])
    if 'gwp_manufacturing_ratio' in extracted:
        result['gwp_manufacturing_ratio'] = round(float(extracted['gwp_manufacturing_ratio'])/100,3)
    if 'gwp_use_ratio' in extracted:
        result['gwp_use_ratio'] = round(float(extracted['gwp_use_ratio'])/100,3)
    if 'gwp_eol_ratio' in extracted:
        result['gwp_eol_ratio'] = round(float(extracted['gwp_eol_ratio'])/100,3)
    if 'gwp_transport_ratio' in extracted:
        result['gwp_transport_ratio'] = round(float(extracted['gwp_transport_ratio'])/100,3)  
    now = datetime.datetime.now()
    result['added_date'] = now.strftime('%Y-%m-%d')
    result['add_method'] = "Dell Auto Parser"

    if not 'gwp_use_ratio' in extracted:
        unpie = piechart_analyser.PiechartAnalyzer(debug=2)

        pie_data: Dict[str, Any] = {}
        for image in pdf.list_images(body):
            unpie_output = unpie.analyze(image, ocrprofile='DELL')
            if unpie_output and len(unpie_output.keys()) > len(pie_data.keys()):
                # print(unpie_output)
                pie_data = unpie_output
                if 'use' in pie_data and 'prod' in pie_data:
                    break
        if pie_data:
            result = unpie.append_to_boavizta(result, pie_data)

    yield data.DeviceCarbonFootprint(result)


# Convenient way to run this scraper as a standalone.
if __name__ == '__main__':
    loader.main(parse)
