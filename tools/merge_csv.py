"""Merge two csv file while reporting and dealing with conflicts."""
import csv
import argparse
import sys
import re
from typing import List, Optional, Dict, Set
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

def get_key(device: dict, key_name: str) -> str:
    assert key_name in device
    if key_name == 'sources':
        pdf_file = re.search(r'([^\/]*\.pdf)', device.get(key_name, ""))
        assert pdf_file is not None
        return pdf_file[0]
    return device.get(key_name, "").lower()

def main(string_args: Optional[List[str]] = None) -> None:
    argparser = argparse.ArgumentParser(
        description='Merge two Boavizta csv file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    argparser.add_argument('files', nargs='+', help='Oldest to newest .csv files (in case of conflict, priority will be given to the newest files).')
    argparser.add_argument('-v', '--verbose', default=0, type=int, help='Verbosity level (0=none, 1=print automatic conflict resolutions, 2=print pedantic warnings')
    argparser.add_argument('-i', '--interactive', action='store_true', help='Ask user how ot resolve conflicts')
    argparser.add_argument('-k', '--key', default='name', help='Name of the field used to find duplicates')
    argparser.add_argument('-o', '--output', help='Output .csv file')
    args = argparser.parse_args(string_args)
    conflict = 'interactive' if args.interactive else 'keep2nd'
    nb_files = len(args.files)
    result :Dict[str,data.DeviceCarbonFootprint] = {}
    origins :Dict[str,Set[int]] = {}
    nb_truly_clean_fusions = 0
    nb_clean_fusions_with_conflicts = 0
    nb_mixed_fusions = 0
    nb_attributes_in_mixed_fusions = 0
    nb_duplicates = [0]*nb_files
    conflict_count :Dict[str,int] = {}

    for i in reversed(range(nb_files)):
        devices = load_csv(args.files[i])
        for device in reversed(devices):
            key = get_key(device, args.key)
            if key in result:
                # merge the twos while giving priority to the one that is already present in result
                device2 = result[key]
                result[key],report,conflicts = data.DeviceCarbonFootprint.merge(device, device2, conflict=conflict, verbose=args.verbose)
                # record stats on conflicts
                for conflict in conflicts:
                    if conflict in conflict_count:
                        conflict_count[conflict] += 1
                    else:
                        conflict_count[conflict] = 0
                if i in origins[key]:
                    nb_duplicates[i] += 1
                else:
                    # we had a collision
                    if len(report[0])==0:
                        # in this case, device2 has been left unchanged
                        if len(conflicts)==0:
                            nb_truly_clean_fusions += 1
                        else:
                            nb_clean_fusions_with_conflicts += 1
                    else:
                        # in this case some attributes have been gathered from the older device
                        nb_mixed_fusions += 1
                        nb_attributes_in_mixed_fusions += len(report[0])
                        if args.verbose>=1:
                            print(key,": gather old attributes for",report[0])
            else:
                result[key] = device
                origins[key] = set()
            origins[key].add(i)
    
    content = data.DeviceCarbonFootprint.csv_headers()
    for device in result.values():
        content += device.reorder().as_csv_row()
    if args.output and args.output!="-":
        with open(args.output, 'w', encoding='utf-8') as output:
            output.write(content)
    else:
        sys.stdout.write(content)
    
    nb_singletons = [0]*nb_files
    for i in range(nb_files):
        nb_singletons[i] = sum(map(lambda x: len(x)==1 and i in x, origins.values()))
    print("\n------------------------------------------------------------")
    print(  "| Summary report                                           |")
    print(  "------------------------------------------------------------")
    print(  "Number of singletons: ", nb_singletons, sep='')
    print(  "Number of self duplicates: ", nb_duplicates, sep='')
    print(  "Number of truly clean fusions:            ", nb_truly_clean_fusions, sep='')
    print(  "Number of clean fusions hiding conflicts: ", nb_clean_fusions_with_conflicts, sep='')
    print(  "Number of mixed fusions:                  ", nb_mixed_fusions, sep='')
    print(  "Number of attributes gathered from the oldest data: ", nb_attributes_in_mixed_fusions, sep='')
    print(  "Details on conflicts:")
    for k,n in conflict_count.items():
        print("  ", k, "x", n)
    print(  "------------------------------------------------------------")

if __name__ == '__main__':
    main()