from re import compile, search
from locale import atof
from collections import Counter
from typing import Union
from datetime import datetime

from ..dividends_interface import DividendsInterface
from .dividends_total import DividendsTotal

class Dividends(DividendsInterface):

    columns = ["security", "cusip", "transaction_date", "amount", "transaction_type"]

    _date_pattern = compile(f"^\d\d\/\d\d\/\d\d$")
    _quantity_pattern = compile(f"^-?\d?\d?\d(,\d\d\d)*\.\d+$")

    _security_pattern = compile("[0-9A-Z ]+") # purposefully ignores securities that are named with (cont'd)
    _cusip_pattern = compile("[0-9A-Z]{9}")
    _subtotal_pattern = compile("^Total.*")

    # these are random strings I've noticed that get parsed strangely -- should be part of the transaction type
    _notes_exclusions = ["-Various"]


    def __init__(self, data: list, include_notes: bool, disqualified: bool = False):
        if include_notes:
            self.columns.append("notes")

        super().__init__(data, self.columns)

        self.include_notes = include_notes
        self.disqualified = disqualified

        assert(isinstance(data, list))
        # == Columns ==
        assert(isinstance(data[0], str)) # security
        assert(isinstance(data[1], str)) # cusip
        date_search = search(Dividends._date_pattern, data[2])
        assert(date_search is not None) # transaction_date
        self.date = datetime.strptime(date_search.group(0), "%m/%d/%y")

        assert(Dividends._quantity_pattern.match(data[3])) # amount
        assert(isinstance(data[4], str)) # transaction_type
        if (include_notes):
            assert(isinstance(data[5], str)) # notes

    def disqualify(self, shares_disqualified, share_dividend_amount) -> "DividendsInterface":
        '''Produces a new Dividend of type 'nonqualified dividend' and adjusts this dividend accordingly'''
        disqualification_amount = round(shares_disqualified * share_dividend_amount, 2)
        dividend_data = [self.get("security"), self.get("cusip"), \
                self.get("transaction_date"), str(disqualification_amount), "Nonqualified dividend"]
        if self.include_notes:
            dividend_data.append(self.get("notes"))

        disqualified_dividend = Dividends(dividend_data, self.include_notes, disqualified = True)

        # update in place to adjust for disqualification
        amount_idx = self.columns.index("amount")
        parsed_amount = atof(self.data[amount_idx])
        new_qualified_amount = parsed_amount - disqualification_amount
        assert(new_qualified_amount >= 0)
        self.data[amount_idx] = str(new_qualified_amount)

        return disqualified_dividend

    def copy(self) -> "DividendsInterface":
        return Dividends(self.data.copy(), self.include_notes)

    @staticmethod
    def parse(raw_data: "list[str]", include_notes: bool) -> "list[Dividends]":
        transx: list[Dividends] = []
        assert(isinstance(raw_data, list))
        if not raw_data: return transx  # empty list

        def error(parsed, parsing, value):
            raise Exception(f"Error while parsing {parsing} ({value}) for (partial) dividend transaction {parsed}")

        security = raw_data[0].strip()
        cusip = raw_data[1].strip()

        subtotals = {}
        grand_total = None

        cursor = 2
        while cursor < len(raw_data):
            # dividends transactions begin with a date and contain at least three fields
            if Dividends._date_pattern.match(raw_data[cursor]) and cursor <= len(raw_data) - 3:
                date = raw_data[cursor]
                cursor += 1
            elif Dividends._subtotal_pattern.match(raw_data[cursor]) \
                and Dividends._quantity_pattern.match(raw_data[cursor-1]):
                subtotals, grand_total = Dividends.parse_totals(raw_data, cursor)
                break
            else:
                cursor += 1
                continue

            dividend_raw = [security, cusip, date]
            # amount
            if Dividends._quantity_pattern.match(raw_data[cursor]):
                dividend_raw.append(raw_data[cursor])
                cursor += 1
            else:
                error(dividend_raw, "amount", raw_data[cursor])

            # type
            dividend_raw.append(raw_data[cursor])
            cursor += 1

            if (include_notes):
                # if no notes, add an empty string. because there may not be notes, also verify we're not out of bounds
                # also add empty string if the value at the cursor is in the exclusions list,
                # or if the next value indicates a subtotal section (in which case the value is an amount)
                if cursor < len(raw_data) and Dividends._date_pattern.match(raw_data[cursor]) or \
                    raw_data[cursor] in Dividends._notes_exclusions or \
                    cursor + 1 < len(raw_data) and Dividends._subtotal_pattern.match(raw_data[cursor+1]):
                    dividend_raw.append("")
                else:
                    dividend_raw.append(raw_data[cursor])
                    cursor += 1 # only increment the cursor if there were notes, otherwise we want to pick up with the discovered date

            transx.append(Dividends(dividend_raw, include_notes))

            del dividend_raw

        calculated_subtotals = {}
        map = {}
        for transaction in transx:
            type = transaction.get("transaction_type")
            if type not in map:
                for subtotal_type in subtotals.keys():
                    type_for_match = search("Total (.*)", subtotal_type).group(1) # type:ignore since "Total " is guaranteed
                    if type_for_match in type or type in type_for_match:
                        map[type] = subtotal_type
                if type not in map:
                    map[type] = "Total Dividends & distributions" # the catchall
                if map[type] not in calculated_subtotals:
                    calculated_subtotals[map[type]] = 0

            calculated_subtotals[map[type]] += atof(transaction.get("amount"))

        for subtotal_type in subtotals.keys():
            if(round(subtotals[subtotal_type], 2) != round(calculated_subtotals[subtotal_type], 2)):
                expected = "\n".join([f"{type}: {amount}" for type, amount in subtotals.items()])
                actual = "\n".join([f"{type}: {amount}" for type, amount in calculated_subtotals.items()])
                raise Exception(f"Error while parsing Dividends for security {security}. Got\n{actual} but expected\n{expected}")

        # todo -- figure out how to properly store the grand total for final validation. I suspect bad design

        return transx

    @staticmethod
    def parse_totals(raw_data, cursor) -> "tuple[dict[str, float], Union[DividendsTotal, None]]":
        subtotals_pairs = []
        new_cursor = cursor
        while new_cursor < len(raw_data) and Dividends._subtotal_pattern.match(raw_data[new_cursor]):
            subtotal_amount = atof(raw_data[new_cursor-1])
            subtotals_pairs.append([raw_data[new_cursor], subtotal_amount])
            new_cursor += 2
            continue

        #detect when the subtotals give way to grand total
        grand_total = None
        grand_total_idx = len(subtotals_pairs)
        counter = Counter([x[0] for x in subtotals_pairs])
        if (counter.most_common(1)[0][1] > 1):
            keys = [x[0] for x in subtotals_pairs]
            # this key always comes first, so find the first instance (ignoring potentially the start of the subtotals)
            grand_total_idx = keys.index("Total Dividends & distributions", 1)
            grand_total = Dividends.parse_grand_totals(raw_data, cursor + 2*grand_total_idx)

        subtotals: "dict[str, float]" = {}
        for i in range(grand_total_idx):
            key, value = subtotals_pairs[i]
            subtotals[key] = value
        return (subtotals, grand_total)

    @staticmethod
    def parse_grand_totals(raw_data, cursor) -> DividendsTotal:
        subtotals = {}
        while cursor < len(raw_data):
            if Dividends._subtotal_pattern.match(raw_data[cursor]) \
                    and Dividends._quantity_pattern.match(raw_data[cursor-1]):
                subtotal_amount = atof(raw_data[cursor-1])
                subtotals[raw_data[cursor]] = subtotal_amount
            cursor += 1

        total_title = "Total Dividends & distributions"
        tax_exempt_title = "Total Tax-exempt dividends"
        foreign_tax_withheld_title = "Total Foreign tax withheld"
        if total_title not in subtotals:
            subtotals[total_title] = 0
        if tax_exempt_title not in subtotals:
            subtotals[tax_exempt_title] = 0
        if foreign_tax_withheld_title not in subtotals:
            subtotals[foreign_tax_withheld_title] = 0
        
        return DividendsTotal(subtotals["Total Dividends & distributions"], \
            tax_exempt=subtotals["Total Tax-exempt dividends"], \
            foreign_tax_withheld=subtotals["Total Foreign tax withheld"])
