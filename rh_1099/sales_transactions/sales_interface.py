
class SalesInterface:


    def __init__(self, data: list, columns: list):
        assert(len(data) == len(self.columns))
        self.data = data
        self.columns = columns

    
    def get(self, key):
        col = self.columns.index(key)
        return self.data[col]


    @staticmethod
    def parse(raw_data: list) -> list:
        pass
