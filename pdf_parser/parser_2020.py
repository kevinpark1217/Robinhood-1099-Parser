from .parser_interface import ParserInterface
from .transx import Transx


class Parser2020(ParserInterface):
    
    def __init__(self, pdf_path):
        super().__init__(pdf_path)
        self.pandas_options = { "header": None }
    
    def process(self):
        keystr = "Proceeds from Broker and Barter Exchange Transactions"
        num_pages = len(self.pages)

        last_raw_entries = []
        for p in range(1, num_pages+1):
        # Test pages: 7,8,23-26
        # for p in range(7, 8+1):
            if self.contains(keystr, p):
                print("Page: {}".format(str(p)))

                strings = self.viewer.canvas.strings
                # print(self.viewer.canvas.text_content) # contains format information
                
                prev_idx = -1
                while idx := next((i for i, val in enumerate(strings[prev_idx+1:]) if "Symbol:" in val and "CUSIP:" in val), None):
                    
                    if prev_idx >= 0:
                        raw_entries = last_raw_entries + strings[prev_idx:prev_idx+idx+1]
                        last_raw_entries = []
                        Transx.parse(raw_entries)
                    elif "(cont'd)" not in strings[prev_idx+idx+1] and last_raw_entries:
                            Transx.parse(last_raw_entries)
                            last_raw_entries = []

                    # Next Iteration
                    prev_idx += idx + 1
                    
                # Last entry of the page // concatentate
                last_raw_entries += strings[prev_idx:]
                # print(raw_entries)

        Transx.parse(last_raw_entries)