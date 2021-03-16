import io, csv

from .sales_transactions import SalesInterface

class PDFContents():


    def __init__(self):
        self.sales = []


    def add_sales(self, sales):
        assert(isinstance(sales, list))
        for sale in sales:
            assert(isinstance(sale, SalesInterface))
        self.sales += sales

    
    def total(self, key):
        # Calculates total sum of data[key] of all sales
        # Assumes that data is number
        total = 0.
        for sale in self.sales:
            if not (val := sale.get(key)): continue
            val = val.replace(',','').split()[0] # remove commas and trailing characters
            total += float(val)
        return total


    def empty(self) -> bool:
        if not self.sales: return True
        return False


    def to_csv(self, csv_path):
        if self.empty():
            raise Exception("No data to write as CSV file")

        # Write to CSV
        with open(csv_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(self.sales[0].columns)
            for sale in self.sales:
                writer.writerow(sale.data)
