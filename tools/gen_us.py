import re
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("-s", "--source", required=True, help="CSV file to be converted")
argparser.add_argument("-o", "--output", required=True, help="output CSV file")
args = vars(argparser.parse_args())
source = args["source"]
output = args["output"]
o = open(output, 'w')
s = open(source, 'r')
content = s.read()
content = re.sub(r'([0-9]+)\,([0-9]+\%*)', r'\1.\2', content)
content = re.sub(r';', r',', content)
o.write(content)
o.close()
s.close()