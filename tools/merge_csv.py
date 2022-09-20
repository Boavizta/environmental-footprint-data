"""Merge two csv file while reporting and dealing with conflicts."""
import csv
import argparse
import sys
import re
from typing import List, Optional, Dict
from tools.parsers.lib import data

# FIXME: this could be done in DeviceCarbonFootprint.from_text?
def clean_device(data: Dict[str, str]) -> Dict[str, str]:
    result = data

    if 'memory' in result:
        result['memory'] = re.sub(r'(?i)GB', '', result['memory'])
    
    locs = {
        'China': 'CN',
        'Worldwide': 'WW',
        'Germany': 'DE'
    }
    for l in ['use_location','assembly_location']:
        if l in result and result[l] in locs.keys():
            result[l] = locs[result[l]]

    return result

def load_csv(filename: str):
    with open(filename, 'rt', encoding='utf-8') as file:
        csvreader = csv.DictReader(file)
        return [data.DeviceCarbonFootprint.from_text(clean_device(row)) for row in csvreader]

def main(string_args: Optional[List[str]] = None) -> None:
    argparser = argparse.ArgumentParser(
        description='Merge two Boavizta csv file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        exit_on_error=False)
    argparser.add_argument('files', nargs=2, help='Oldest and newest .csv files (in case of conflict, priority will be given to the newest file).')
    argparser.add_argument('-v', '--verbose', action='store_true', help='Print automatic conflict resolutions')
    argparser.add_argument('-i', '--interactive', action='store_true', help='Ask user how ot resolve conflicts')
    argparser.add_argument('-o', '--output', help='Output .csv file')
    args = argparser.parse_args(string_args)
    conflict = 'interactive' if args.interactive else 'keep2nd'
    devices = load_csv(args.files[1]) + load_csv(args.files[0])
    result = dict()
    for device in devices:
        key = device.get('name').lower()
        if key in result:
            # merge the twos while giving priority to the one that is already present in result
            device2 = result[key]
            result[key] = data.DeviceCarbonFootprint.merge(device, device2, conflict=conflict, verbose=args.verbose)
        else:
            result[key] = device
    
    content = data.DeviceCarbonFootprint.csv_headers()
    for device in result.values():
        content += device.reorder().as_csv_row()
    if args.output and args.output!="-":
        with open(args.output, 'w', encoding='utf-8') as output:
            output.write(content)
    else:
        sys.stdout.write(content)

if __name__ == '__main__':
    main()