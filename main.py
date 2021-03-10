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
parser.add_argument('--check', action='store_true', help='Print total values to check')

args = parser.parse_args()
if not args.csv:
    args.csv = 'output.csv'


from pdf_parser import Parser2020
parser = Parser2020(args.pdf_path)
transx = parser.process(not args.silent)


# Print values to crosscheck with PDF
if args.check:
    proceeds = cost = wash_sales_loss = gain_loss = 0
    for trnx in transx:
        proceeds += round(trnx.get_proceeds() * 100)
        cost += round(trnx.get_cost() * 100)
        wash_sales_loss += round(trnx.get_wash_sales_loss() * 100)
        gain_loss += round(trnx.get_gain_loss() * 100)

    proceeds /= 100
    cost /= 100
    wash_sales_loss /= 100
    gain_loss /= 100

    print("Calculated Totals:")
    print("=== Make sure the values matches with the PDF totals! ===")
    print(f"proceeds: {proceeds}, cost: {cost}, wash_sales_loss: {wash_sales_loss}, gain_loss: {gain_loss}")


# Write to CSV
with open(args.csv, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(Transx.columns)
    for trnx in transx:
        trnx.write_csv(writer)

# print(args.pdf)
# print(args.)
