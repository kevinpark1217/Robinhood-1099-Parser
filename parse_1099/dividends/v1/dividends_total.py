from ..dividends_interface import DividendsInterface

from locale import atof

class DividendsTotal():

    def __init__(self, nonqualified: float = 0.0, qualified: float = 0.0, \
        foreign_tax_withheld: float = 0.0, tax_exempt: float = 0.0, \
        section_199a: float = 0.0, disqualified: float = 0.0):
        self.nonqualified = nonqualified
        self.qualified = qualified
        self.foreign_tax_withheld = foreign_tax_withheld
        self.tax_exempt = tax_exempt
        self.section_199a = section_199a
        self.disqualified = disqualified

    @staticmethod
    def FromDividends(dividends: "list[DividendsInterface]"):
        keys = ["Nonqualified dividend", "Qualified dividend", \
            "Foreign tax withheld", "Tax-exempt dividend", "Section 199A dividend"]
        data = {key: 0.0 for key in keys}
        disqualified_sum = 0.0

        for dividend in dividends:
            for key in keys:
                if key in dividend.get("transaction_type"):
                    amount = atof(dividend.get("amount"))
                    data[key] += amount
                    if dividend.disqualified:
                        disqualified_sum += amount

        # flip sign on withheld since it shouldn't show negative
        return DividendsTotal(data[keys[0]], data[keys[1]], -1 * data[keys[2]], data[keys[3]], data[keys[4]], disqualified_sum)

    def __str__(self):
        total: float = self.nonqualified + self.qualified + self.section_199a
        adjusted = "Adjusted " if self.disqualified > 0 else ""
        return f"{'='*10} {adjusted}Dividends {'='*10}" \
            + f"\n    1a Total ordinary dividends:  ${total:,.2f}" \
            + f"\n    1b Qualified dividends:       ${self.qualified:,.2f}" \
            + f"\n     5 Section 199A dividends     ${self.section_199a:,.2f}" \
            + f"\n     7 Foreign tax paid:          ${self.foreign_tax_withheld:,.2f}" \
            + f"\n    12 Exempt-interest dividends: ${self.tax_exempt:,.2f}"

