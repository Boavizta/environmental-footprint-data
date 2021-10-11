import csv
import re
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("-s", "--source", required=True, help="CSV file to be converted")
argparser.add_argument("-o", "--output", required=True, help="output CSV file")
args = vars(argparser.parse_args())
source = args["source"]
output = args["output"]

output = open(output, 'w')
writer = csv.writer(output, delimiter=';')
with open(source) as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        updatedrow = [re.sub(r'(.*[0-9]*)\.([0-9].*)', r'\1,\2', content) for content in row]
        updatedrow = [re.sub(r'(.*[0-9]*)\.([0-9].*(in|TB|GB))', r'\1,\2', content) for content in updatedrow]
        writer.writerow(updatedrow)
output.close()
