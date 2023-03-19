from tqdm import tqdm
from pdfreader.viewer.canvas import SimpleCanvas
from re import compile
from typing import Union

from ...subparser_interface import SubparserInterface
from ...pdf_contents import PDFContents
from .dividends import Dividends


class DividendsParser(SubparserInterface):

    _security_pattern = compile("[0-9a-zA-Z ]+")
    _cusip_symbol_pattern = compile("[0-9A-Z]{9}") # purposefully ignores securities followed by (cont'd)

    def __init__(self, pdf_file):
        super().__init__(pdf_file)

    def process(self, show_progress: bool, pdf_contents: PDFContents) -> PDFContents:
        indicator_str = "Detail for Dividends and Distributions"
        num_pages = len(self.pages)

        page_iter = range(1, num_pages+1)
        if show_progress:
            page_iter = tqdm(page_iter, desc='Pages')
        for p in page_iter:
            if self.contains(indicator_str, p):
                canvas: SimpleCanvas = self.viewer.canvas #type:ignore
                strings = canvas.strings
                if strings is None:
                    # no need to error log, this just appeases the linter. `contains` relies on strings being not-None
                    continue

                def get_next_security_index(strings, start_idx = 0) -> Union[int, None]:
                    for i in range(start_idx, len(strings)-1):
                        if DividendsParser._security_pattern.match(strings[i]) and DividendsParser._cusip_symbol_pattern.match(strings[i+1]):
                            return i

                security_header_idx = get_next_security_index(strings)
                while security_header_idx:
                    security_name = strings[security_header_idx]
                    # todo: fix multi-line securities names. Unfortunately, the previous string can often be a false match
                    if (security_header_idx > 0 and DividendsParser._security_pattern.match(strings[security_header_idx-1])):
                        security_name = strings[security_header_idx-1] + security_name
                    print(security_header_idx, security_name)
                    security_header_idx = get_next_security_index(strings, security_header_idx+1)

        return pdf_contents