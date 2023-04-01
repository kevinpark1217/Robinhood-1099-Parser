import io, csv

from .sales.sales_interface import SalesInterface
from .sales.v1.sales_total import SalesTotal
from .dividends.dividends_interface import DividendsInterface
from .dividends.v1.dividends_total import DividendsTotal

class PDFContents():

    def __init__(self):
        self.sales: list[SalesInterface] = []
        self.dividends: list[DividendsInterface] = []


    def add_sales(self, sales):
        assert(isinstance(sales, list))
        for sale in sales:
            assert(isinstance(sale, SalesInterface))
        self.sales += sales

    def add_dividends(self, dividends):
        assert(isinstance(dividends, list))
        for dividend in dividends:
            assert(isinstance(dividend, DividendsInterface))
        self.dividends += dividends

    def display_validation(self):
        # prints validation strings for stored transactions
        dividends_total = DividendsTotal.FromDividends(self.dividends)
        sales_total = SalesTotal(self.sales)
        print(">>> Calculated Totals:")
        print("    Make sure the values match with the PDF totals!")
        print(sales_total)
        print(dividends_total)


    def empty(self) -> bool:
        if not self.sales and not self.dividends: return True
        return False

