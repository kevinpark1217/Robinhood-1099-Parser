
from ..dividends.dividends_interface import DividendsInterface
from ..sales.sales_interface import SalesInterface

from typing import Union
from csv import writer

class CSVWriter():

    def write_to_csv(self, filename: str, data_set: "Union[list[DividendsInterface], list[SalesInterface]]"):
        with open(filename, 'w') as f:
            csv_writer = writer(f)
            csv_writer.writerow(data_set[0].columns)
            for row in data_set:
                csv_writer.writerow(row.data)
        print(f">>> Saved to {filename}")