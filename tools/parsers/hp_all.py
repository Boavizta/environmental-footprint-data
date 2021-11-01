"""Parsers for HP DESK PDF.

See an example here https://h22235.www2.hp.com/hpinfo/globalcitizenship/environment/productdata/Countries/_MultiCountry/productcarbonfootprint_notebo_2020116223055953.pdf
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


def parse(body: BinaryIO, pdf_filename: str) -> Iterator[data.DeviceCarbonFootprint]:
    result = data.DeviceCarbonFootprintData()
    result['manufacturer'] = 'HP'

    # Parse text from PDF.
    pdf_as_text = pdf.pdf2txt(body)
    extracted = text.search_all_patterns(_HP_DESK_PATTERNS, pdf_as_text)
    if not extracted:
        logging.error('The file "%s" did not match the HP pattern', pdf_filename)
        return

    # Convert each matched group to our format.
    if 'name' in extracted:
        result['name'] = extracted['name'].strip()
    if 'footprint_with_error' in extracted and 'tolerance' in extracted:
        result['gwp_total'] = float(extracted['footprint_with_error'])
        result['gwp_error_ratio'] = round((float(extracted['tolerance']) / result['gwp_total']), 4)
    if 'footprint' in extracted:
        result['gwp_total'] = float(extracted['footprint'])
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
    now = datetime.datetime.now()
    result['added_date'] = now.strftime('%Y-%m-%d')
    result['add_method'] = "HP Auto Parser"

    # TODO(pascal): Explore images to pull out Use and Manufacturing percentages.

    yield data.DeviceCarbonFootprint(result)


# Convenient way to run this scraper as a standalone.
if __name__ == '__main__':
    loader.main(parse)
