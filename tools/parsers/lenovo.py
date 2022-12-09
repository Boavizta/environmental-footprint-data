"""Parsers for Lenovo LCA PDF.

See an example here https://static.lenovo.com/ww/docs/regulatory/eco-declaration/pcf-lenovo-e41-45.pdf
"""

import logging
import re
import datetime
from typing import BinaryIO, Iterator, Dict, Any

from tools.parsers.lib import data
from tools.parsers.lib import loader
from tools.parsers.lib import pdf
from tools.parsers.lib import text
from tools.parsers.lib import piechart_analyser

# A list of patterns to search in the text.
_LENOVO_LCA_PATTERNS = (
    re.compile(r'Commercial\s*Name\s*(?P<name>.*?)\s*Model'),
    re.compile(r'Issue\s*Date\s*(?P<date>[A-Z][a-z][0-9]*, [0-9]{4})'),
    re.compile(r'Issue\s*Date\s*(?P<date>[0-9]{4}-[0-9]*-[0-9])*'),
    re.compile(r'report\s*this\s*value\s*as\s*(?P<footprint>[0-9]+\.?[0-9]*)\s*'),
    re.compile(r'\+\/-\s*(?P<error>[0-9]+)\s*kg'),
    re.compile(r'Product\s*Weight\s*kg\s*(Input\s*)?(?P<weight>[0-9]*\.[0-9]*)'),
    re.compile(r'Screen\s*Size\s*inches\s*(?P<screen_size>[0-9]+\.[0-9]+)'),
    re.compile(r'Assembly\s*Location\s*no unit\s*(?P<assembly_location>[A-Za-z]*)\s+'),
    re.compile(r'Product\s*Lifetime\s*years\s*(Input\s*)?(?P<lifetime>[0-9]*)'),
    re.compile(r'Use\s*Location\s*no\s*unit\s*(?P<use_location>[A-Za-z]*)\s+'),
    re.compile(r'.*Use\s*(?P<gwp_use>[0-9]*\.*[0-9]*)\%.*')
)

_USE_PERCENT_PATTERN = re.compile(r'.*Use([0-9]*\.*[0-9]*)\%.*')


def parse(body: BinaryIO, pdf_filename: str) -> Iterator[data.DeviceCarbonFootprint]:
    result = data.DeviceCarbonFootprintData()
    result['manufacturer'] = 'Lenovo'

    # Parse text from PDF.
    pdf_as_text = pdf.pdf2txt(body)
    extracted = text.search_all_patterns(_LENOVO_LCA_PATTERNS, pdf_as_text)
    if not extracted:
        logging.error('The file "%s" did not match the Lenovo pattern', pdf_filename)
        return

    # Convert each matched group to our format.
    if 'name' in extracted:
        result['name'] = extracted['name'].strip().removeprefix('Lenovo ').replace(',','')
    if 'footprint' in extracted:
        result['gwp_total'] = float(extracted['footprint'])
    else:
        raise ValueError((repr(pdf_as_text), extracted))
    if result.get('gwp_total') and 'error' in extracted:
        result['gwp_error_ratio'] = round((float(extracted['error']) / result['gwp_total']), 3)
    if 'date' in extracted:
        result['report_date'] = extracted['date']
    if 'weight' in extracted:
        result['weight'] = float(extracted['weight'])
    if 'screen_size' in extracted:
        result['screen_size'] = float(extracted['screen_size'])
    if 'assembly_location' in extracted:
        result['assembly_location'] = extracted['assembly_location']
    if 'lifetime' in extracted:
        result['lifetime'] = float(extracted['lifetime'])
    if 'use_location' in extracted:
        result['use_location'] = extracted['use_location']
    if 'energy_demand' in extracted:
        result['yearly_tec'] = float(extracted['energy_demand'])
    if 'hdd' in extracted:
        result['hard_drive'] = extracted['hdd']
    if 'ram' in extracted:
        result['memory'] = float(extracted['ram'])
    if 'cpu' in extracted:
        result['number_cpu'] = int(extracted['cpu'])
    now = datetime.datetime.now()
    result['added_date'] = now.strftime('%Y-%m-%d')
    result['add_method'] = "Lenovo Auto Parser"

    if 'gwp_use' in extracted:
        result['gwp_use_ratio'] = int(extracted['gwp_use'])/100
    else:
        unpie = piechart_analyser.PiechartAnalyzer(debug=0)

        pie_data: Dict[str, Any] = {}
        for image in pdf.list_images(body):
            unpie_output = unpie.analyze(image, ocrprofile='Lenovo')
            if unpie_output and len(unpie_output.keys()) > len(pie_data.keys()):
                # print(unpie_output)
                pie_data = unpie_output
                if 'use' in pie_data and 'prod' in pie_data:
                    break
        if not pie_data:
            # try with full page rendering
            image = pdf.pdf2img(body, 0)
            rows, columns, depth = image.shape
            crop = image[:int(rows/2), int(columns/2):, :].copy()
            pie_data = unpie.analyze(crop, ocrprofile='Lenovo')
            print(pie_data)
        if pie_data:
            result = unpie.append_to_boavizta(result, pie_data)

    yield data.DeviceCarbonFootprint(result)


# Convenient way to run this scraper as a standalone.
if __name__ == '__main__':
    loader.main(parse)
