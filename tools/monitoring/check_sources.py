import csv
import logging
from typing import Any, Optional
import requests
import hashlib
from tools.parsers.lib import data

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

with open('boavizta-data-us.csv', 'rt', encoding='utf-8') as existing_file:
    csvfile = csv.DictReader(existing_file)
    seen = set()
    for row in csvfile:
        result=data.DeviceCarbonFootprint(row)
        if row.get('sources'):
            pdf=requests.get(result.data['sources'])
            if pdf.status_code == 200:
                open('./tempfile.pdf', 'wb').write(pdf.content)
                result.data['sources_hash']=md5('./tempfile.pdf')
                if row.get('name') in seen:
                    result.data['name']=row.get('name') + " - Duplicate"
                else:
                    seen.add(row.get('name'))
            else:
                result.data['sources_hash']="Unreachable"
            print(result.as_csv_row())