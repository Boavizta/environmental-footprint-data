from csv import DictReader
from distutils.log import error
import re
import datetime
from typing import BinaryIO, Iterator

from tools.parsers.lib import data
from tools.parsers.lib.image import crop, find_text_in_image, image_to_text
from tools.parsers.lib import loader
from tools.parsers.lib import pdf
from tools.parsers.lib import text
import requests
import io
from tools.parsers import dell_laptop

result = data.DeviceCarbonFootprintData()

# open file in read mode
with open('boavizta-data-us.csv', 'r') as read_obj:
    # pass the file object to reader() to get the reader object
    csv_dict_reader = DictReader(read_obj)
    # Iterate over each row in the csv using reader object
    for row in csv_dict_reader:
        # row variable is a list that represents a row in csv
        if ( row['manufacturer'] == "Dell" ):
            pdf_path = row['sources']
            if re.search('http(s)*\:\/\/*.', pdf_path):
                open('./tempfile.pdf', 'wb').write(requests.get(pdf_path).content)
                url=pdf_path
                pdf_path = "./tempfile.pdf"

            with open(pdf_path, 'rb') as fh:
                for result in dell_laptop.parse(io.BytesIO(fh.read()), url):
                        if result:
                            device=result.data
                            device['source']=row['sources']
                        else:
                            device['source']="error"
                            device["name"]="error"
                            
            device['manufacturer'] = 'Dell'
            newline=device["manufacturer"] + "," + (device["name"] if "name" in device else '') + "," + row["name"] + "," + (device["category"] if "category" in device else '') + "," + row["category"] + "," + (device["subcategory"] if "subcategory" in device else '') + "," + row["subcategory"] + "," + (str(device["gwp_total"]) if "gwp_total" in device else '') + "," + str(row["gwp_total"]) + "," + (str(device["gwp_use_ratio"]) if "gwp_use_ratio" in device else '') + "," + str(row["gwp_use_ratio"]) + "," + (str(device["yearly_tec"]) if "yearly_tec" in device else '') + "," + str(row["yearly_tec"]) + "," + (str(device["lifetime"]) if "lifetime" in device else '') + "," + str(row["lifetime"]) + "," + (device["use_location"] if "use_location" in device else '') + "," + str(row["use_location"]) + "," + (device["report_date"].replace(",","") if "report_date" in device else '') + "," + str(row["report_date"]) + "," + device["source"] + "," + row["source"] + "," + (str(device["gwp_error_ratio"]) if "gwp_error_ratio" in device else '') + "," + str(row["gwp_error_ratio"]) + "," + (str(device["gwp_manufacturing_ratio"]) if "gwp_manufacturing_ratio" in device else '') + "," + str(row["gwp_manufacturing_ratio"]) + "," + (str(device["weight"]) if "weight" in device else '') + "," + str(row["weight"]) + "," + (device["assembly_location"] if "assembly_location" in device else '') + "," + str(row["assembly_location"]) + "," + (str(device["screen_size"]) if "screen_size" in device else '') + "," + str(row["screen_size"]) + ",,,,,," + device["added_date"] + "," + device["add_method"] + "," + (str(device["gwp_transport_ratio"]) if "gwp_transport_ratio" in device else '') + "," + str(row["gwp_transport_ratio"]) + "," + (str(device["gwp_eol_ratio"]) if "gwp_eol_ratio" in device else '')  + "," + str(row["gwp_eol_ratio"])
            print(newline)
    quit()