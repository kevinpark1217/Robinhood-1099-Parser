from tqdm import tqdm
from pdfreader.viewer.canvas import SimpleCanvas
from re import compile
from typing import Union

from ...subparser_interface import SubparserInterface
from ...pdf_contents import PDFContents
from .dividends import Dividends


class DividendsParser(SubparserInterface):

    _transaction_type_pattern = compile(".*(dividend|withheld).*")

    def __init__(self, pdf_file, include_dividend_notes: bool = False):
        super().__init__(pdf_file)
        self.include_notes = include_dividend_notes

    def process(self, show_progress: bool, pdf_contents: PDFContents) -> PDFContents:
        indicator_str = "Detail for Dividends and Distributions"
        num_pages = len(self.pages)

        dangling_lines: list[str] = []

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
                        if Dividends._security_pattern.match(strings[i]) and Dividends._cusip_pattern.match(strings[i+1]):
                            return i

                # robinhood header can look like a security header since their account ids are the same form as CUSIPs
                # endeavor to pass over these false matches by advancing at least as far as the title, which in the current version gets beyond the robinhood account string
                header_title_idx = strings.index(indicator_str)
                prev_header_idx: int = -1
                security_header_idx = get_next_security_index(strings, header_title_idx+1)
                while security_header_idx:
                    # fix multi-line securities names. Not ideal, could improve
                    if (security_header_idx > 0 and \
                        Dividends._security_pattern.match(strings[security_header_idx-1]) and \
                        not Dividends._subtotal_pattern.match(strings[security_header_idx-1]) and \
                        not DividendsParser._transaction_type_pattern.match(strings[security_header_idx-1])): # in the case where there's just one dividend for a security, there isn't a subtotal
                        strings[security_header_idx] = f"{strings[security_header_idx-1]} {strings[security_header_idx]}"

                    # case: this isn't the first header on the page
                    if prev_header_idx >= 0:
                        # action: previous security is finished, parse its range of lines into a Sales
                        security_dividends_lines = dangling_lines + strings[prev_header_idx:security_header_idx]
                        dangling_lines = []
                        pdf_contents.add_dividends(Dividends.parse(security_dividends_lines, self.include_notes))

                    # case: this is the first header on the page
                    else:
                        # action: previous security (if it exists) is finished. Try to parse it as a Dividends just in case
                        contd_idx = 0
                        try:
                            contd_idx = strings.index("(cont'd)")
                        except ValueError:
                            contd_idx = 0

                        pdf_contents.add_dividends(Dividends.parse(dangling_lines + strings[contd_idx:security_header_idx], self.include_notes))
                        dangling_lines = []
                    
                    prev_header_idx = security_header_idx
                    security_header_idx = get_next_security_index(strings, security_header_idx+1)

                # case: no security headers remain but lines do. Capture them for future handling
                dangling_lines += strings[prev_header_idx:]

        # case: no pages nor security headers remain but the last security needs to be parsed out. Do it
        pdf_contents.add_dividends(Dividends.parse(dangling_lines, self.include_notes))
        return pdf_contents