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
import argparse
import requests
import io
from tools.parsers import microsoft


argparser = argparse.ArgumentParser()
result = data.DeviceCarbonFootprintData()
argparser.add_argument("-s", "--source", required=True, help="URL to .pdf to be converted")
args = vars(argparser.parse_args())
pdf_path = args["source"]
url = ""
if re.search('http(s)*\:\/\/*.', pdf_path):
    open('./tempfile.pdf', 'wb').write(requests.get(pdf_path).content)
    url=pdf_path
    pdf_path = "./tempfile.pdf"

with open(pdf_path, 'rb') as fh:
     for result in microsoft.parse(io.BytesIO(fh.read()), url):
            device=result.data
device['manufacturer'] = 'Microsoft'
device['source']=url
newline=device["manufacturer"] + "," + device["name"] + "," + device["category"] + "," + device["subcategory"] + "," + str(device["gwp_total"]) + "," + (str(device["gwp_use_ratio"]) if "gwp_use_ratio" in device else '') + "," + str(device["yearly_tec"]) + "," + str(device["lifetime"]) + "," + device["use_location"] + "," + device["report_date"].replace(",","") + "," + device["source"] + "," + (str(device["gwp_error_ratio"]) if "gwp_error_ratio" in device else '') + "," + (str(device["gwp_manufacturing_ratio"]) if "gwp_manufacturing_ratio" in device else '') + "," + str(device["weight"]) + "," + device["assembly_location"] + "," + str(device["screen_size"]) + ",,,,,," + device["added_date"] + "," + device["add_method"] + "," + (str(device["gwp_transport_ratio"]) if "gwp_transport_ratio" in device else '') + "," + (str(device["gwp_eol_ratio"]) if "gwp_eol_ratio" in device else '')
print(newline)
quit()