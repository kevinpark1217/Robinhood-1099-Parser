import argparse
import os
import os.path
import csv

from pdf_parser.transx import Transx


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg


parser = argparse.ArgumentParser(
    description='Robinhood Securities 1099 Tax Document Parser')
parser.add_argument('--pdf', required=True, dest='pdf_path',
                    help='Input path to the 1099 PDF document', metavar="FILE",
                    type=lambda x: is_valid_file(parser, x))
parser.add_argument('--csv', metavar="FILE", help='Output path of the parsed CSV')
parser.add_argument('--silent', action='store_true', help='Hide progress bar')

args = parser.parse_args()
if not args.csv:
    args.csv = 'output.csv'


from pdf_parser import Parser2020
parser = Parser2020(args.pdf_path)
transx = parser.process(not args.silent)

with open(args.csv, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(Transx.columns)
    for trnx in transx:
        trnx.write_csv(writer)

# print(args.pdf)
# print(args.)
