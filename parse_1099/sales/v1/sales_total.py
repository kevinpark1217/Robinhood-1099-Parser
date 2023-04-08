from ..sales_interface import SalesInterface

class SalesTotal():

    def __init__(self, sales: "list[SalesInterface]"):
        keys = ["proceeds", "cost", "wash_sales_loss", "gain_loss"]
        data = {key: 0.0 for key in keys}

        for sale in sales:
            for key in keys:
                val = sale.get(key)
                if not val: continue
                val = val.replace(',','').split()[0] # remove commas and trailing characters
                data[key] += float(val)
        
        self.proceeds = data["proceeds"]
        self.cost = data["cost"]
        self.wash_sales_loss = data["wash_sales_loss"]
        self.gain_loss = data["gain_loss"]

    def __str__(self):
        return f"{'='*10} Brokerage Transactions {'='*10}" \
            + f"\n    proceeds:        ${self.proceeds:,.2f}" \
            + f"\n    cost:            ${self.cost:,.2f}" \
            + f"\n    wash sales loss: ${self.wash_sales_loss:,.2f}" \
            + f"\n    gain / loss:     ${self.gain_loss:,.2f}"

