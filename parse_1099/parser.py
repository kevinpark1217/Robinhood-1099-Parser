from .pdf_contents import PDFContents
from .sales.v1.sales_parser import SalesParser
from .dividends.v1.dividends_parser import DividendsParser


class Parser:

    def __init__(self, pdf_path, include_dividend_notes):
        fd = open(pdf_path, "rb")

        self.subparsers = [ \
            SalesParser(fd), \
            DividendsParser(fd, include_dividend_notes)]

    def parse(self, show_progress: bool) -> PDFContents:
        contents = PDFContents()
        for parser in self.subparsers:
            contents = parser.process(show_progress, contents)
        return contents
