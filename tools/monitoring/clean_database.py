import csv
import logging
from typing import Any, Optional
import requests
import sys
from tools.parsers.lib import data
from typing import List, Optional, Dict, Set
import argparse


def main(string_args: Optional[List[str]] = None) -> None:
    argparser = argparse.ArgumentParser(
            description='Cleanup a Boavizta csv file',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    argparser.add_argument('-f', '--file', help='.csv file to clean')
    argparser.add_argument('-v', '--verbose', default=0, type=int, help='Verbosity level (0=none, 1=print automatic conflict resolutions, 2=print pedantic warnings')
    argparser.add_argument('-i', '--interactive', action='store_true', help='Ask user how ot resolve conflicts')
    argparser.add_argument('-o', '--output', help='Output .csv file')
    args = argparser.parse_args(string_args)
    conflict = 'interactive' if args.interactive else 'keep2nd'
    content = data.DeviceCarbonFootprint.csv_headers()
    with open(args.file, 'rt', encoding='utf-8') as existing_file:
        csvfile = csv.DictReader(existing_file)
        seen = []
        for row in csvfile:
            result=data.DeviceCarbonFootprint(row)
            if not 'comment' in result.data:
                result.data['comment']=""
            if row.get('sources'):
                pdf=requests.get(result.data['sources'], headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"})
                unreach=False
                if ( pdf.status_code == 200 ) and not ('error' in pdf.url) and not ('404' in pdf.url):
                    open('./tempfile.pdf', 'wb').write(pdf.content)
                    if 'sources_hash' in result.data:
                        if not result.data['sources_hash'] == "":
                            tempmd5=data.md5_file('./tempfile.pdf')
                            if not tempmd5 == result.data['sources_hash']:
                                result.data['comment']=result.data['comment'] + "File " + result.data['sources'] + " changed."
                        else:
                            result.data['sources_hash']=data.md5_file('./tempfile.pdf')
                            result.data['comment']=result.data['comment'] + " MD5 hash added"
                    else:
                        result.data['sources_hash']=data.md5_file('./tempfile.pdf')
                        result.data['comment']=result.data['comment'] + " MD5 hash added"
                else:
                    result.data['comment']=result.data['comment'] + " Source is unreachable"
                    unreach=True
                notseen=True
                if not unreach:
                    for i in seen:
                        if row.get('name') == i.data["name"]:
                            notseen=False
                            new_result,report = data.DeviceCarbonFootprint.merge(i, result, conflict=conflict, verbose=args.verbose)
                            new_result.data['comment']= result.data['comment'] + " merged"
                            seen.remove(i)
                            content += new_result.reorder().as_csv_row()
                            print(new_result.reorder().as_csv_row())
                            # Ne gere pas le cas de plus de 2 doublons
                if notseen:
                    seen.append(result)
                    print(result.reorder().as_csv_row())
        
        for device in seen:
            content += device.reorder().as_csv_row()
        if args.output and args.output!="-":
            with open(args.output, 'w', encoding='utf-8') as output:
                output.write(content)
        else:
            sys.stdout.write(content)

if __name__ == '__main__':
    main()