from tqdm import tqdm
from pdfreader.viewer.canvas import SimpleCanvas

from ...subparser_interface import SubparserInterface
from ...pdf_contents import PDFContents
from .sales import Sales


class SalesParser(SubparserInterface):
    
    def __init__(self, pdf_file):
        super().__init__(pdf_file)

    def process(self, show_progress: bool, pdf_contents: PDFContents) -> PDFContents:
        indicator_str = "Proceeds from Broker and Barter Exchange Transactions"
        num_pages = len(self.pages)

        dangling_lines = []
        
        page_iter = range(1, num_pages+1)
        if show_progress:
            page_iter = tqdm(page_iter, desc='Pages')
        for p in page_iter:
            if self.contains(indicator_str, p):
                canvas: SimpleCanvas = self.viewer.canvas #type: ignore
                strings = canvas.strings
                
                if strings is None:
                    # no need to error log, this just appeases the linter. `contains` relies on strings being not-None
                    continue

                prev_header_idx: int = -1
                security_header_line_indices = [i for i, val in enumerate(strings) if "Symbol:" in val and "CUSIP:" in val]
                for header_idx in security_header_line_indices:
                    # case: this isn't the first header on the page
                    if prev_header_idx >= 0:
                        # action: previous security is finished, parse its range of lines into a Sales
                        security_transaction_lines = dangling_lines + strings[prev_header_idx:header_idx]
                        dangling_lines = []
                        pdf_contents.add_sales(Sales.parse(security_transaction_lines))

                    # case: this is the first header on the page and it isn't a 'continued'
                    elif "(cont'd)" not in strings[header_idx]:
                        # action: previous security (if it exists) is finished. Try to parse it as a Sales just in case
                        pdf_contents.add_sales(Sales.parse(dangling_lines))
                        dangling_lines = []
                    
                    # todo: suppose there are two cont'd. consider
                    prev_header_idx = header_idx

                # case: no security headers remain but lines do. Capture them for future handling
                dangling_lines += strings[prev_header_idx:]

        # case: no pages nor security headers remain but the last security needs to be parsed out. Do it
        pdf_contents.add_sales(Sales.parse(dangling_lines))
        return pdf_contents