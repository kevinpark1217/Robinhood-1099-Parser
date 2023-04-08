import argparse
import os
import os.path
import locale

from .pdf_contents import PDFContents
from .parser import Parser
from .dividends.dividend_analyzer import DividendAnalyzer
from .utilities.csv_writer import CSVWriter
from .dividends.v1.dividends_total import DividendsTotal

locale.setlocale(locale.LC_ALL, '')

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg


def main():
    arg_parser = argparse.ArgumentParser(
        prog='parse_1099',
        description='1099 Tax Document Parser')
    arg_parser.add_argument('-i', '--pdf', required=True, dest='pdf_path',
                        help='Input path to the 1099 PDF document', metavar="FILE",
                        type=lambda x: is_valid_file(arg_parser, x))
    arg_parser.add_argument('-o', '--csv', metavar="PREFIX", help='Output path (and prefix) of the parsed CSVs. For example, ./directory/output will produce ./directory/output_sales.csv and ./directory/output_dividends.csv')
    arg_parser.add_argument('-s', '--silent', action='store_true', help='Hide progress bar')
    arg_parser.add_argument('-v', '--validate', action='store_true', help='Print total values for validation')
    arg_parser.add_argument('-n', "--include-dividend-notes", action='store_true', help="Include the 'notes' column in the dividend output csv")
    arg_parser.add_argument('-d', "--disable-dividend-analysis", action='store_true', help="Disable analysis of qualified dividend holding periods")
    arg_parser.add_argument('-r', "--analysis-report", action='store_true', help="Produce a detailed report from the qualified dividends analysis.")

    args = arg_parser.parse_args()
    if not args.csv:
        args.csv = 'output'


    parser = Parser(args.pdf_path, args.include_dividend_notes)
    contents: PDFContents = parser.parse(not args.silent)

    # Print values to crosscheck with PDF
    if args.validate:
        contents.display_validation()

    # Save as csv file
    if not contents.empty():
        sales_csv = f"{args.csv}_sales.csv"
        dividends_csv = f"{args.csv}_dividends.csv"

        csv_writer = CSVWriter()

        if (contents.sales is not None):
            csv_writer.write_to_csv(sales_csv, contents.sales)
        if (contents.dividends is not None):
            csv_writer.write_to_csv(dividends_csv, contents.dividends)

            if not args.disable_dividend_analysis:
                dividend_analyzer = DividendAnalyzer()
                if args.analysis_report:
                    dividend_analyzer.enable_reporting(args.csv)
                adjusted_dividends, adjusted_total = dividend_analyzer.get_disqualified_dividends(contents)
                if adjusted_dividends is not None:
                    assert(adjusted_total is not None) # this should never be none if there are dividends
                    report = "For more details, see the sales_with_short_holding_periods report." if args.analysis_report else "For more details, use the --analysis-report flag."
                    print(f">>> Analyzed dividends and determinded that ${adjusted_total.disqualified:.2f} of qualified dividends should be considered nonqualified due to \
                          short holding periods around the ex-dividend date. The disqualification is reflected in the adjusted_dividends csv. {report}")
                    adjusted_dividends_csv = f"{args.csv}_adjusted_dividends.csv"
                    csv_writer.write_to_csv(adjusted_dividends_csv, adjusted_dividends)

                    if args.validate:
                        print(adjusted_total)
    else:
        print(f">>> No data to save to file")