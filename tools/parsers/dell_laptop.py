"""Parsers for Dell LCA PDF.

See an example here https://i.dell.com/sites/csdocuments/CorpComm_Docs/en/carbon-footprint-wyse-3030.pdf
"""
import logging
import re
import datetime
from typing import BinaryIO, Iterator

from tools.parsers.lib import data
from tools.parsers.lib.image import crop, find_text_in_image, image_to_text
from tools.parsers.lib import loader
from tools.parsers.lib import pdf
from tools.parsers.lib import text
from matplotlib import pyplot as plt


# A list of patterns to search in the text.
_DELL_LCA_PATTERNS = (
    re.compile(r' (?P<name>.*?)\s*From design to end-of-life'),
    re.compile(r' page 1 (?P<name>.*?)\s*From design to end-of-life'),
    re.compile(r'(?P<name>VxRail.*?)\s*Report'),
    re.compile(r' estimated carbon footprint\: \s*(?P<footprint>[0-9]*) kgCO2e(?: \+\/\- (?P<error>[0-9]*)\s*kgCO2e)?'),
    re.compile(r' estimated ?standard deviation (of )?\+\/\- (?P<error>[0-9]*)\s*kgCO2e'),
    re.compile(r'mean of (?P<footprint>[0-9]+)\s*kg'),
    re.compile(r'standard deviation of (?P<error>[0-9]+)\s*kg'),
    re.compile(r' Report produced\s*(?P<date>[A-Z][a-z]*,* [0-9]{4}) '),
    re.compile(r' Product Weight\s*(?P<weight>[0-9]*.[0-9]*)\s*kg'),
    re.compile(r' Screen Size\s*(?P<screen_size>[0-9]*)'),
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
        result['hard_drive'] = extracted['hdd']
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
        use_ok=False
        manuf_ok=False
        eol_ok=False
        transport_ok=False
        for image in pdf.list_images(body):
            #plt.imshow(image, interpolation='nearest', ) 
            #plt.show()
            use_thsh, manuf_thsh, eol_thsh, transport_thsh, thsh = 150, 150, 150, 150, 150
            while ((use_ok == False) and (manuf_ok == False) and (eol_ok == False) and (transport_ok == False) and thsh > 10):
                thsh= thsh - 10
                if use_ok == False:
                    use_block = find_text_in_image(image, re.compile('Use'), threshold=thsh)
                    use_thsh = thsh
                if manuf_ok == False:
                    manuf_block = find_text_in_image(image, re.compile(r'(M?)anufa(cturing?)'), threshold=thsh)
                    manuf_thsh = thsh
                if eol_ok == False:
                    eol_block = find_text_in_image(image, re.compile(r'E(o|O|0)L'), threshold=thsh)
                    eol_thsh = thsh
                if transport_ok == False:
                    transport_block = find_text_in_image(image, re.compile(r'(T?)ransp(ortation?)'), threshold=thsh)
                    transport_thsh = thsh

            if use_block and (use_ok == False):
                use_ok=True
                # Create an image a bit larger, especially below the text found where the number is.
                use_image = image[
                    use_block.top - 1:use_block.top + use_block.height * 3 + 3,
                    use_block.left - 20:use_block.left + use_block.width + 20,
                ]
                # Usefull to debug when Use ratio cannot be retrieved
                #plt.imshow(use_image, interpolation='nearest') 
                #plt.show()
                use_text = image_to_text(use_image, threshold=use_thsh)
                clean_text = use_text.replace('\n', '').replace(' ', '')
                match_use = _USE_PERCENT_PATTERN.match(clean_text)
                if match_use:
                    result['gwp_use_ratio'] = round(float(match_use.group(1))/100,3)
            if manuf_block and (manuf_ok == False):
                manuf_ok=True
                # Create an image a bit larger, especially below the text found where the number is.
                manuf_image = image[
                    manuf_block.top - 1:manuf_block.top + manuf_block.height * 3,
                    manuf_block.left - 8:manuf_block.left + manuf_block.width + 3,
                ]
                #plt.imshow(manuf_image, interpolation='nearest') 
                #plt.show()
                manuf_text = image_to_text(manuf_image, threshold=manuf_thsh)
                clean_text = manuf_text.replace('\n', '').replace(' ', '')
                match_manuf = _MANUF_PERCENT_PATTERN.match(clean_text)
                if match_manuf:
                    result['gwp_manufacturing_ratio'] = round(float(match_manuf.group(1))/100,3)
            if eol_block and (eol_ok == False):
                eol_ok=True
                # Create an image a bit larger, especially below the text found where the number is.
                eol_image = image[
                    eol_block.top - 1:eol_block.top + eol_block.height * 3 + 3,
                    eol_block.left - 10:eol_block.left + eol_block.width + 20,
                ]
                #plt.imshow(eol_image, interpolation='nearest') 
                #plt.show()
                eol_text = image_to_text(eol_image, threshold=eol_thsh)
                clean_text = eol_text.replace('\n', '').replace(' ', '')
                match_eol = _EOL_PERCENT_PATTERN.match(clean_text)
                if match_eol:
                    result['gwp_eol_ratio'] = round(float(match_eol.group(1))/100,3)
            if transport_block and (transport_ok == False):
                transport_ok=True
                transport_image = image[
                    transport_block.top - 1:transport_block.top + transport_block.height * 3 + 3,
                    transport_block.left:transport_block.left + transport_block.width + 20,
                ]
                #plt.imshow(transport_image, interpolation='nearest') 
                #plt.show()
                transport_text = image_to_text(transport_image, threshold=transport_thsh)
                clean_text = transport_text.replace('\n', '').replace(' ', '')
                #print(clean_text)
                match_transport = _TRANSPORT_PERCENT_PATTERN.match(clean_text)
                if match_transport:
                    result['gwp_transport_ratio'] = round(float(match_transport.group(1))/100,3)
            if ('gwp_use_ratio' in result and 'gwp_manuf_ratio' in result):
                break

    yield data.DeviceCarbonFootprint(result)


# Convenient way to run this scraper as a standalone.
if __name__ == '__main__':
    loader.main(parse)
