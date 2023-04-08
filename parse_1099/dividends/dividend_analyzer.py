from datetime import datetime
from pandas.core.series import Series
from re import search, compile
from typing import Union, Tuple
from locale import atof

from .dividends_interface import DividendsInterface
from .dividends_repository_interface import DividendsRepositoryInterface
from .dividends_repository_interface import By
from .v1.dividends_repository import DividendsRepository
from .v1.dividends_total import DividendsTotal
from ..pdf_contents import PDFContents
from ..sales.sales_interface import SalesInterface
from ..utilities.csv_writer import CSVWriter


class DividendAnalyzer():

    _cusip_pattern = compile("CUSIP: ([0-9A-Z]{9})")
    _symbol_pattern = compile("SYMBOL: ([A-Z]{3,4})")

    def __init__(self):
        self.repository: DividendsRepositoryInterface = DividendsRepository()
        self.report_prefix: Union[str, None] = None
        self.csv_writer: CSVWriter = CSVWriter()

    def enable_reporting(self, report_prefix: str):
        self.report_prefix = report_prefix

    def get_disqualified_dividends(self, contents: PDFContents) -> "Tuple[Union[list[DividendsInterface], None], Union[DividendsTotal, None]]":
        '''Gets an adjusted list of dividends, or None if there were no disqualifications'''
        # get securities that had qualified dividends
        cusips = DividendAnalyzer.get_securities_with_qualified_dividends(contents.dividends)
        adjusted_total = None
        adjusted_dividends = None

        if len(cusips) > 0:
            # get sales for those securities and calculate holding period
            transactions_with_short_holding_periods = DividendAnalyzer.get_securities_with_short_holding_periods(contents.sales, cusips)
            symbols_with_short_holding_periods = [s.symbol for s in transactions_with_short_holding_periods if s.symbol is not None]
            cusips_with_short_holding_periods = [s.cusip for s in transactions_with_short_holding_periods if s.symbol is None and s.cusip is not None]

            # fetch dividend information for all securities with holding periods less than 60 days
            prev_year = datetime.now().year - 1
            cusip_exdates, cusip_to_symbol_map = self.repository.get_dividend_exdates(By.CUSIP, cusips_with_short_holding_periods, prev_year)
            symbol_exdates, _ = self.repository.get_dividend_exdates(By.SYMBOL, symbols_with_short_holding_periods, prev_year)

            dividend_exdates = None
            if (cusip_exdates is not None and symbol_exdates is not None):
                dividend_exdates = cusip_exdates.append(symbol_exdates)
            elif (cusip_exdates is not None):
                dividend_exdates = cusip_exdates
            elif (symbol_exdates is not None):
                dividend_exdates = symbol_exdates

            if dividend_exdates is None:
                raise Exception("Encountered an error while retreiving ex-dividend dates")

            # produce an updated list of dividends
            cusip_to_symbol_map.update([(s.cusip, s.symbol) for s in transactions_with_short_holding_periods if s.symbol is not None and s.cusip is not None])

            adjusted_dividends = self.get_adjusted_dividends(contents.dividends, transactions_with_short_holding_periods, dividend_exdates, cusip_to_symbol_map)
            if adjusted_dividends is not None:
                adjusted_total = DividendsTotal.FromDividends(adjusted_dividends)

        return adjusted_dividends, adjusted_total

    def get_adjusted_dividends(self, dividends: "list[DividendsInterface]",
                               sales_with_short_holding_periods: "list[SalesInterface]",
                               dividend_exdates: Series, cusip_to_symbol: "dict[str, str]") -> Union["list[DividendsInterface]", None]:

        # for each cusip, get all relevant dividends
        # - for each dividend
        # -- get the exdate
        # -- get short sales where the acquisition date < ex-date < disposal date
        # -- count those shares and produce a disqualified dividend for the original dividend. Update a copy of the original dividend accordingly

        adjusted_dividends: list[DividendsInterface] = []
        adjustment_occurred = False
        detailed_report: list[SalesInterface] = []

        cusips = set([dividend.get("cusip") for dividend in dividends])
        for cusip in cusips:
            cusip_dividends: list[DividendsInterface] = [
                dividend for dividend in dividends if dividend.get("cusip") == cusip]
            if (cusip in cusip_to_symbol):
                # case where the cusip had qualified dividends, perform analysis
                symbol = cusip_to_symbol[cusip]

                cusip_exdates = dividend_exdates[symbol]

                for dividend in cusip_dividends:
                    working_dividend = dividend.copy()
                    adjusted_dividends.append(working_dividend)

                    if not dividend.get("transaction_type").startswith("Qualified"):
                        # skip all except the qualified dividends when analyzing for disqualified dividends
                        continue

                    related_dividends = [cusip_div for cusip_div in cusip_dividends
                                            if dividend.date == cusip_div.date]
                    
                    parsed_related_dividend_amounts = [atof(div.get("amount")) for div in related_dividends]
                    total_dividend_amount = sum([amount for amount in parsed_related_dividend_amounts if amount > 0]) # excludes taxes withheld
                    qualified_percent = atof(working_dividend.get("amount")) / total_dividend_amount

                    exdate = DividendAnalyzer.get_dividend_exdate(
                        working_dividend, cusip_exdates)
                    disqualified_sales = [sale for sale in sales_with_short_holding_periods
                                          if sale.cusip == cusip and
                                          sale.acquired_date <= exdate and exdate <= sale.disposal_date]  # type:ignore since all fields should be populated

                    disqualified_sale_count = len(disqualified_sales)
                    if disqualified_sale_count != 0:
                        adjustment_occurred = True
                        disqualified_shares_count = sum(atof(sale.get("quantity")) for sale in disqualified_sales)

                        amount_per_share = cusip_exdates[exdate.date()]
                        disqualified_dividend = working_dividend.disqualify(
                            disqualified_shares_count, amount_per_share * qualified_percent)
                        adjusted_dividends.append(disqualified_dividend)

                        if self.report_prefix is not None:
                            for sale in disqualified_sales:
                                sale.add_note(f"Disqualifies dividend {dividend} with exdate {exdate}, payout ${amount_per_share} and qualified percentage {round(qualified_percent*100, 1)}%")
                            detailed_report.extend(disqualified_sales)

                if self.report_prefix is not None:
                    qualified_sales = [sale for sale in sales_with_short_holding_periods
                                       if sale.cusip == cusip and sale not in detailed_report]
                    for sale in qualified_sales:
                        sale.add_note("")
                    detailed_report.extend(qualified_sales)
            else:
                # case where the cusip doesn't have qualified dividends
                # add the dividends and don't bother with copying, they won't be modified
                adjusted_dividends.extend(cusip_dividends)

        if self.report_prefix is not None:
            assert(len(sales_with_short_holding_periods) == len(detailed_report))
            self.csv_writer.write_to_csv(f"{self.report_prefix}_sales_with_short_holding_periods.csv", detailed_report)

        return adjusted_dividends if adjustment_occurred else None

    @staticmethod
    def get_securities_with_qualified_dividends(dividends: "list[DividendsInterface]") -> "set[str]":
        securities: set[str] = set()
        for dividend in dividends:
            div_type = dividend.get("transaction_type")
            div_cusip = dividend.get("cusip")
            if div_cusip not in securities and "Qualified dividend" in div_type and "Non" not in div_type:
                securities.add(div_cusip)
        return securities

    @staticmethod
    def get_securities_with_short_holding_periods(sales: "list[SalesInterface]", relevant_cusips: "set[str]") -> "list[SalesInterface]":
        relevant_securities: list[SalesInterface] = []
        for sale in sales:
            sale_desc = sale.get("description")
            sale_cusip = None
            sale_symbol = None

            sale_cusip_search = search(DividendAnalyzer._cusip_pattern, sale_desc)
            if (sale_cusip_search):
                sale_cusip = sale_cusip_search.group(1)
            sale_symbol_search = search(DividendAnalyzer._symbol_pattern, sale_desc)
            if (sale_symbol_search):
                sale_symbol = sale_symbol_search.group(1)

            if sale_cusip is None:
                raise Exception(f"Could not parse CUSIP for security '{sale_desc}'")

            if sale_cusip not in relevant_cusips:
                # only perform holding period analysis for qualified dividends
                continue

            acquisition_date = datetime.strptime(sale.get("acquired_date"), "%m/%d/%y")
            disposal_date = datetime.strptime(sale.get("sold_date"), "%m/%d/%y")

            # update sales in-place for future retreival
            sale.cusip = sale_cusip
            sale.symbol = sale_symbol
            sale.acquired_date = acquisition_date
            sale.disposal_date = disposal_date

            # https://www.fidelity.com/tax-information/tax-topics/qualified-dividends
            # You must have held those shares of stock unhedged for at least 61 days
            # out of the 121-day period that began 60 days before the ex-dividend date.
            if (disposal_date - acquisition_date).days < 61:
                relevant_securities.append(sale)

        return relevant_securities

    @staticmethod
    def get_dividend_exdate(dividend: DividendsInterface, dividend_exdates: Series) -> datetime:
        max_exdate: datetime = datetime(1, 1, 1)
        for exdate in dividend_exdates.keys():
            reformatted_exdate = datetime(exdate.year, exdate.month, exdate.day)
            if reformatted_exdate > max_exdate and reformatted_exdate < dividend.date:
                max_exdate = reformatted_exdate
            else:
                break
        return max_exdate