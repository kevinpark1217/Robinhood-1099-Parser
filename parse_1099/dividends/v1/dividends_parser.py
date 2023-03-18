from tqdm import tqdm

from ...subparser_interface import SubparserInterface
from ...pdf_contents import PDFContents
from .dividends import Dividends


class DividendsParser(SubparserInterface):
    
    def __init__(self, pdf_file):
        super().__init__(pdf_file)

    def process(self, show_progress: bool, pdf_contents: PDFContents) -> PDFContents:
        indicator_str = "Proceeds from Broker and Barter Exchange Transactions"
        num_pages = len(self.pages)

        last_raw_entries = []
        
        page_iter = range(1, num_pages+1)
        if show_progress:
            page_iter = tqdm(page_iter, desc='Pages')
        for p in page_iter:
            if self.contains(indicator_str, p):

                strings = self.viewer.canvas.strings
                # print(self.viewer.canvas.text_content) # contains format information
                
                prev_idx = -1
                def getNextIndex():
                    return next((i for i, val in enumerate(strings[prev_idx+1:]) if "Symbol:" in val and "CUSIP:" in val), None)
                idx = getNextIndex()
                while idx:
                    if prev_idx >= 0:
                        raw_entries = last_raw_entries + strings[prev_idx:prev_idx+idx+1]
                        last_raw_entries = []
                        pdf_contents.add_dividends(Dividends2020.parse(raw_entries))
                    elif "(cont'd)" not in strings[prev_idx+idx+1]:
                        pdf_contents.add_dividends(Dividends2020.parse(last_raw_entries))
                        last_raw_entries = []

                    # Next Iteration
                    prev_idx += idx + 1
                    idx = getNextIndex()
                    
                # Last entry of the page // concatentate
                last_raw_entries += strings[prev_idx:]

        pdf_contents.add_dividends(Dividends2020.parse(last_raw_entries))
        return pdf_contents