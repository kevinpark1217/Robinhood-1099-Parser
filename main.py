import argparse
import os
import os.path


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'rb')  # return an open file handle


parser = argparse.ArgumentParser(
    description='Robinhood Securities 1099 Tax Document Parser')
parser.add_argument('--pdf', required=True, dest='pdf_fd',
                    help='Input path to the 1099 PDF document', metavar="FILE",
                    type=lambda x: is_valid_file(parser, x))
parser.add_argument('--csv', help='Output path of the parsed CSV')

args = parser.parse_args()


from pdf_parser import Parser2020
parser = Parser2020(args.pdf_fd)
parser.test()

# print(args.pdf)
# print(args.)
