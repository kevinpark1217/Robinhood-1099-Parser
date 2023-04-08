from datetime import datetime

class DividendsInterface:

    def __init__(self, data: list, columns: list):
        assert(len(data) == len(self.columns))
        self.data = data
        self.columns = columns
        self.date = datetime(1, 1, 1)
        self.disqualified = False

    def disqualify(self, shares_disqualified, share_dividend_amount) -> "DividendsInterface": #type:ignore
        pass

    def get(self, key):
        col_idx = self.columns.index(key)
        return self.data[col_idx]

    def copy(self) -> "DividendsInterface": #type:ignore
        pass

    @staticmethod
    def parse(raw_data: list) -> list: #type: ignore
        pass

    def __str__(self) -> str:
        return f"{self.get('security')}: {self.get('cusip')} | {self.get('transaction_type')} | {self.get('amount')} | {self.get('transaction_date')}"
