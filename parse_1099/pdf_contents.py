import io, csv

from .sales.sales_interface import SalesInterface
from .dividends.dividends_interface import DividendsInterface

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

    def total(self, key):
        # Calculates total sum of data[key] of all sales
        # Assumes that data is number
        total = 0.
        for sale in self.sales:
            val = sale.get(key)
            if not val: continue
            val = val.replace(',','').split()[0] # remove commas and trailing characters
            total += float(val)
        return total


    def empty(self) -> bool:
        if not self.sales and not self.dividends: return True
        return False


    def to_csv(self, csv_prefix):
        if self.empty():
            raise Exception("No data to write as CSV file")

        # Write to CSV
        if (self.sales):
            sales_csv = f"{csv_prefix}_sales.csv"
            with open(sales_csv, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(self.sales[0].columns)
                for sale in self.sales:
                    writer.writerow(sale.data)

        if (self.dividends):
            dividends_csv = f"{csv_prefix}_dividends.csv"
            with open(dividends_csv, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(self.dividends[0].columns)
                for dividend in self.dividends:
                    writer.writerow(dividend.data)
