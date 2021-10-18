"""Parsers for HP DESK PDF.

See an example here https://i.dell.com/sites/csdocuments/CorpComm_Docs/en/carbon-footprint-wyse-3030.pdf
"""

import logging
import sys
import re
import datetime
from typing import BinaryIO, Dict, Iterator

from .lib import data
from .lib.image import binary_grey_threshold, crop, find_text_in_image, image_to_text
from .lib import loader
from .lib import pdf


# A list of patterns to search in the text.
_HP_DESK_PATTERNS = (
    re.compile(r'\s\sProduct carbon footprint (?P<name>.*?)\s*Estimated impact'),
    re.compile(r' Estimated impact (?P<footprint>[0-9]*)\s*kgCO2 eq.'),
    re.compile(r' Other organizations might report this value as (?P<footprint_with_error>[0-9]*) \+\/\- (?P<tolerance>[0-9]*) kg of CO2-e'),
    re.compile(r' Lifetime of product\s*(?P<lifetime>[0-9]*) years'),
    re.compile(r' Use location\s*(?P<use_location>[A-Za-z]*)\s+'),
    re.compile(r' Use energy demand \(Yearly TEC\)\s*(?P<energy_demand>[0-9]*.[0-9]*)\s*kWh'),
    re.compile(r' Product weight\s*(?P<weight>[0-9]*.[0-9]*)\s*kg'),
    re.compile(r' Screen size\s*(?P<screen_size>[0-9]*.[0-9]*)\s*inches'),
    re.compile(r' Final manufacturing location\s*(?P<assembly_location>[A-Za-z]*)\s+'),
    re.compile(r' Copyright \s*(?P<date>[0-9]{4}) '),
)

_USE_PERCENT_PATTERN = re.compile(r'.*Use([0-9]*\.*[0-9]*)\%.*')
_MANUF_PERCENT_PATTERN = re.compile(r'.*Manufac(?:turing|uring|ture)([0-9]*\.*[0-9]*)\%.*')


def parse(body: BinaryIO, pdf_filename: str) -> Iterator[data.DeviceCarbonFootprint]:
    result = data.DeviceCarbonFootprintData()
    result['Manufacturer'] = 'HP'

    # Parse text from PDF.
    pdf_as_text = pdf.pdf2txt(body)

    # Match with the specific patterns.
    extracted: Dict[str, str] = {}
    for pattern in _HP_DESK_PATTERNS:
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
    if 'footprint_with_error' in extracted and 'tolerance' in extracted:
        result['Total (kgCO2eq)'] = float(extracted['footprint_with_error'])
        result['Error (%)'] = round((float(extracted['tolerance']) / result['Total (kgCO2eq)'] * 100),2)
    if 'footprint' in extracted:
        result['Total (kgCO2eq)'] = float(extracted['footprint'])
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
    result['Added Date'] = datetime.datetime.now.strftime('%Y-%m-%d')
    result['Add Method'] = "HP Auto Parser"

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
                result['Use (%)'] = float(match_use.group(1))

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
                result['Manufacturing'] = float(match_use.group(1))

        if manuf_block or use_block:
            break

    yield data.DeviceCarbonFootprint(result)


# Convenient way to run this scraper as a standalone.
if __name__ == '__main__':
    loader.main(parse)
