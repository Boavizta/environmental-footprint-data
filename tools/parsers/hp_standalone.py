"""Parsers for HP LCA PDF.

See an example here https://h20195.www2.hp.com/v2/getpdf.aspx/c07779859.pdf
"""
import logging
import re
import datetime
from typing import BinaryIO, Iterator
import os

from tools.parsers.lib import data
from tools.parsers.lib.image import crop, find_text_in_image, image_to_text
from tools.parsers.lib import loader
from tools.parsers.lib import pdf
from tools.parsers.lib import text
import argparse
import requests
import io
from tools.parsers import hp_workplace


argparser = argparse.ArgumentParser()
result = data.DeviceCarbonFootprintData()
argparser.add_argument("-s", "--source", required=True, help="URL to .pdf to be converted")
argparser.add_argument("-c", "--category", required=True, help="Subcategory (Laptop, Monitor, Tablet...)")
argparser.add_argument("-d", "--date", required=False, help="Manufacturing date")
args = vars(argparser.parse_args())
pdf_path = args["source"]
url = ""
if re.search('http(s)*\:\/\/*.', pdf_path):
    open('./tempfile.pdf', 'wb').write(requests.get(pdf_path).content)
    url=pdf_path
    pdf_path = "./tempfile.pdf"
    

with open(pdf_path, 'rb') as fh:
     for result in hp_workplace.parse(io.BytesIO(fh.read()), url):
        result.data['sources_hash']=data.md5_file('./tempfile.pdf')
        result.data['sources']=url
        print(result.as_csv_row())
os.remove('./tempfile.pdf')
quit()