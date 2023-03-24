from re import compile, match

from ..dividends_interface import DividendsInterface

class Dividends(DividendsInterface):

    columns = ["security", "cusip", "transaction_date", "amount", "transaction_type", "notes"]

    _date_pattern = compile(f"^\d\d\/\d\d\/\d\d$")
    _quantity_pattern = compile(f"^-?\d?\d?\d(,\d\d\d)*\.\d+$")

    _security_pattern = compile("[0-9A-Z ]+") # purposefully ignores securities that are named with (cont'd)
    _cusip_pattern = compile("[0-9A-Z]{9}")
    _subtotal_pattern = compile("Total.*")

    # these are random strings I've noticed that get parsed strangely -- should be part of the transaction type
    _notes_exclusions = ["-Various"]


    def __init__(self, data: list):
        super().__init__(data, self.columns)
        assert(isinstance(data, list))
        # == Columns ==
        assert(isinstance(data[0], str)) # security
        assert(isinstance(data[1], str)) # cusip
        assert(Dividends._date_pattern.match(data[2])) # transaction_date
        assert(Dividends._quantity_pattern.match(data[3])) # amount
        assert(isinstance(data[4], str)) # transaction_type
        assert(isinstance(data[5], str)) # notes


    @staticmethod
    def parse(raw_data: list) -> list:
        transx = []
        assert(isinstance(raw_data, list))
        if not raw_data: return transx  # empty list

        def error(parsed, parsing, value):
            raise Exception(f"Error while parsing {parsing} ({value}) for (partial) dividend transaction {parsed}")

        security = raw_data[0].strip()
        cusip = raw_data[1].strip()

        cursor = 2
        while cursor < len(raw_data) - len(Dividends.columns) + 1: # +1 because notes is optional
            # dividends transactions begin with a date
            if Dividends._date_pattern.match(raw_data[cursor]):
                date = raw_data[cursor]
                cursor += 1
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

            transx.append(Dividends(dividend_raw))

            del dividend_raw

        # todo: validate using subtotal section

        return transx