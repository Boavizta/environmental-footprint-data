"""Parsers for Dell LCA PDF.

See an example here https://i.dell.com/sites/csdocuments/CorpComm_Docs/en/carbon-footprint-wyse-3030.pdf
"""

import logging
import sys
import re
import datetime
from typing import BinaryIO, Iterator

from .lib import data
from .lib.image import binary_grey_threshold, crop, find_text_in_image, image_to_text
from .lib import loader
from .lib import pdf



# A list of patterns to search in the text.
_DELL_LCA_PATTERNS = (
    re.compile(r'\s\s(?P<name>.*?)\s*From design to end-of-life'),
    re.compile(r' estimated carbon footprint\: (?P<footprint>[0-9]*) kgCO2e(?: \+\/\- (?P<error>[0-9]*) kgCO2e)?'),
    re.compile(r' estimated standard deviation of \+\/\- (?P<error>[0-9]*)\s*kgCO2e'),
    re.compile(r' Issue Date\s*(?P<date>[A-Z][a-z][0-9]*, [0-9]{4})'),
    re.compile(r' Product Weight\s*kg\s*Input\s*(?P<weight>[0-9]*.[0-9]*)'),
    #re.compile(r' Screen Size\s*inches\s*(?P<screen_size>[0-9]*.[0-9]*'),
    re.compile(r'Assembly Location\s*no unit\s*(?P<assembly_location>[A-Za-z]*)\s+'),
    re.compile(r'Product Lifetime\s*years\s*Input\s*(?P<lifetime>[0-9]*)'),
    re.compile(r' Use Location\s*no unit\s*(?P<use_location>[A-Za-z]*)\s+'),
    re.compile(r' Energy Demand \(Yearly TEC\)\s*(?P<energyè_demand>[0-9]*.[0-9]*)\s*kWh'),
    re.compile(r' HDD\/SSD Quantity (?P<hdd>.*(?:SSD|HDD?))\s+'),
    re.compile(r' DRAM Capacity\s*(?P<ram>[0-9]*)[A-Z]{2}\s+'),
    re.compile(r' CPU Quantity\s*(?P<cpu>[0-9]*)\s+'),
)

_USE_PERCENT_PATTERN = re.compile(r'.*Use([0-9]*\.*[0-9]*)\%.*')
_MANUF_PERCENT_PATTERN = re.compile(r'.*Manufac(?:turing|uring|ture)([0-9]*\.*[0-9]*)\%.*')


def parse(body: BinaryIO, pdf_filename: str) -> Iterator[data.DeviceCarbonFootprint]:
    result = data.DeviceCarbonFootprintData()
    result['Manufacturer'] = 'Dell'

    # Parse text from PDF.
    pdf_as_text = pdf.pdf2txt(body)

    # Match with the specific patterns.
    extracted: dict[str, str] = {}
    for pattern in _DELL_LCA_PATTERNS:
        match = pattern.search(pdf_as_text)
        if not match:
            continue
        for key, value in match.groupdict().items():
            if value:
                extracted[key] = value

    if not extracted:
        logging.error('The file "{pdf_filename}" did not match the Dell pattern')
        return

    # Convert each matched group to our format.
    if 'name' in extracted:
        result['Name'] = extracted['name'].strip()
    if 'footprint' in extracted:
        result['Total (kgCO2eq)'] = float(extracted['footprint'])
    if result.get('Total (kgCO2eq)') and 'error' in extracted:
        result['Error (%)'] = round((float(extracted['error']) / result['Total (kgCO2eq)']),4)
    else:
        raise ValueError(pdf_as_text)
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

    for image in pdf.list_images(body):
        # Search "Use x%" in the left part of the graph.
        cropped_left = crop(image, right=.75)
        use_block = find_text_in_image(cropped_left, re.compile('Use'), threshold=150)
        if use_block:
            # Create an image a bit larger, especially below the text found where the number is.
            use_image = cropped_left[
                use_block.top - 3:use_block.top + use_block.height * 3,
                use_block.left - 20:use_block.left + use_block.width + 20,
            ]
            use_text = image_to_text(use_image, threshold=130)
            clean_text = use_text.replace('\n', '').replace(' ', '')
            match_use = _USE_PERCENT_PATTERN.match(clean_text)
            if match_use:
                result['Use (%)'] = float(match_use.group(1))/100

        # Search "Manufact... x%" in the middle part of the graph.
        cropped_right = crop(image, left=.25, right=.3)
        manuf_block = find_text_in_image(cropped_right, re.compile('Manufa'), threshold=50)
        if manuf_block:
            # Create an image a bit larger, especially below the text found where the number is.
            manuf_image = cropped_right[
                manuf_block.top - 3:manuf_block.top + manuf_block.height * 3,
                manuf_block.left - 8:manuf_block.left + manuf_block.width + 3,
            ]
            manuf_text = image_to_text(manuf_image, threshold=30)
            clean_text = manuf_text.replace('\n', '').replace(' ', '')
            match_use = _MANUF_PERCENT_PATTERN.match(clean_text)
            if match_use:
                result['Manufacturing'] = float(match_use.group(1))/100

        if manuf_block or use_block:
            break

    yield data.DeviceCarbonFootprint(result)


# Convenient way to run this scraper as a standalone.
if __name__ == '__main__':
    loader.main(parse)
