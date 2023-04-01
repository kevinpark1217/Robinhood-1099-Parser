from datetime import datetime
from typing import Union

class SalesInterface:

    def __init__(self, data: list, columns: list):
        assert(len(data) == len(self.columns))
        self.data = data
        self.columns = columns

        self.cusip: "Union[str, None]" = None
        self.symbol: "Union[str, None]" = None
        self.acquired_date: "Union[datetime, None]" = None
        self.disposal_date: "Union[datetime, None]" = None

    def get(self, key):
        col_idx = self.columns.index(key)
        return self.data[col_idx]

    @staticmethod
    def parse(raw_data: list) -> list: # type: ignore
        pass
