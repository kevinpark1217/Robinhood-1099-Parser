from tqdm import tqdm

from .parser_interface import ParserInterface
from ..sales_transactions import Sales2020
from .. import PDFContents


class Parser2020(ParserInterface):
    
    def __init__(self, pdf_path):
        super().__init__(pdf_path)
        self.pandas_options = { "header" : None }
    

    def process(self, show_progress: bool) -> PDFContents:
        keystr = "Proceeds from Broker and Barter Exchange Transactions"
        num_pages = len(self.pages)

        pdf_contents = PDFContents()

        last_raw_entries = []
        
        page_iter = range(1, num_pages+1)
        if show_progress:
            page_iter = tqdm(page_iter, desc='Pages')
        for p in page_iter:
            if self.contains(keystr, p):

                strings = self.viewer.canvas.strings
                # print(self.viewer.canvas.text_content) # contains format information
                
                prev_idx = -1
                while idx := next((i for i, val in enumerate(strings[prev_idx+1:]) if "Symbol:" in val and "CUSIP:" in val), None):
                    
                    if prev_idx >= 0:
                        raw_entries = last_raw_entries + strings[prev_idx:prev_idx+idx+1]
                        last_raw_entries = []
                        pdf_contents.add_sales(Sales2020.parse(raw_entries))
                    elif "(cont'd)" not in strings[prev_idx+idx+1]:
                        pdf_contents.add_sales(Sales2020.parse(last_raw_entries))
                        last_raw_entries = []

                    # Next Iteration
                    prev_idx += idx + 1
                    
                # Last entry of the page // concatentate
                last_raw_entries += strings[prev_idx:]

        pdf_contents.add_sales(Sales2020.parse(last_raw_entries))
        return pdf_contents