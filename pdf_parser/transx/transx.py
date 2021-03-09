import re
import locale


class Transx:

    # == Columns ==
    # descripion
    # sold_date
    # proceeds
    # acquired_date
    # cost
    # wash_sales_loss
    # gain_loss

    def __init__(self, data):
        assert(isinstance(data, list))
        assert(len(data) == 6)


    @staticmethod
    def parse(raw_data):
        assert(isinstance(raw_data, list))
        comma_number_pat = "\d?\d?\d(,\d\d\d)*"
        date_pat = "\d\d\/\d\d\/\d\d"

        date_pattern = re.compile(f"^{date_pat}$")
        quantity_pattern = re.compile(f"^{comma_number_pat}\.\d+$")
        money_pattern = re.compile(f"^\-?{comma_number_pat}\.\d\d$")

    
        desc = raw_data[0]

        shift = 0
        while shift < len(raw_data) - 8:
            if multi := re.match(f"^(?P<cnt>{comma_number_pat}) transactions for (?P<sold_date>{date_pat}).", raw_data[shift+1]):
                # Multiple entries
                cnt = locale.atoi(multi.group("cnt"))
                sold_date = multi.group("sold_date")

                print(f"{cnt} transactions sold on {sold_date}")

                for i in range(cnt):
                    while not (quantity_pattern.match(raw_data[shift+2]) and \
                        money_pattern.match(raw_data[shift+3]) and \
                        date_pattern.match(raw_data[shift+4]) and \
                        money_pattern.match(raw_data[shift+5])): # quantity, proceeds, acquired_date, cost,
                        # money_pattern.match(raw_data[shift+7])): # , ..., gain_loss
                        
                        shift += 1

                    # Wash sales check
                    if raw_data[shift+6] == "...":
                        filtered = raw_data[shift+2:shift+1+7]
                        # Check "i of n"
                        raw_nth = raw_data[shift+1+7]

                        shift += 8

                    elif money_pattern.match(raw_data[shift+6]) and \
                        raw_data[shift+7] == "W":
                        # valid wash sales

                        # Clean wash_sales_loss data
                        filtered = raw_data[shift+2:shift+1+8]
                        filtered[4] += " " + filtered[5]
                        del filtered[5]
                        # Check "i of n"
                        raw_nth = raw_data[shift+1+8]
                        
                        shift += 9

                    else:
                        raise Exception(
                            f"Unknown multi entry format.\n"
                            f"  Exception while parsing...\n"
                            f"  {raw_data[shift+2:shift+1+8]}")
                    
                    # Count check
                    assert(nth_data := re.match(f"^(?P<nth>{comma_number_pat}) of (?P<total>{comma_number_pat})$", raw_nth))
                    assert(locale.atoi(nth_data.group("nth")) == i + 1)
                    assert(locale.atoi(nth_data.group("total")) == cnt)
                    
                    # Add sold_date to the front
                    filtered.insert(0, sold_date)
                    print(filtered)

                    # Clean
                    del raw_nth, filtered

                # shift += 1

            elif date_pattern.match(raw_data[shift+1]) and \
                quantity_pattern.match(raw_data[shift+2]) and \
                money_pattern.match(raw_data[shift+3]) and \
                date_pattern.match(raw_data[shift+4]) and \
                money_pattern.match(raw_data[shift+5]):
                # Single entry
                
                # Wash sales check
                if raw_data[shift+6] == "...":
                    filtered = raw_data[shift+1:shift+1+7]
                    print(filtered)
                    shift += 7

                elif money_pattern.match(raw_data[shift+6]) and \
                    raw_data[shift+7] == "W":
                    # valid wash sales

                    # Clean wash_sales_loss data
                    filtered = raw_data[shift+1:shift+1+8]
                    filtered[5] += " " + filtered[6]
                    del filtered[6]
                    print(filtered)
                    shift += 8

                else:
                    raise Exception(
                        f"Unknown single entry format.\n"
                        f"  Exception while parsing...\n"
                        f"  {raw_data[shift+1:shift+1+8]}")
            else:
                shift += 1
        return

        # Missing edge cases
        multi = re.match(f"^({comma_number_pat}) transactions for ({date_pat}).", raw_data[1])
        if multi:
            # Multiple entries
            cnt = int(multi.group(1))
            sold_date = multi.group(2)

            print(f"{cnt} transactions sold on {sold_date}")
            
            idx = 0
            for i in range(cnt):
                shift = idx
                while not (quantity_pattern.match(raw_data[shift]) and \
                      money_pattern.match(raw_data[shift+1]) and \
                      date_pattern.match(raw_data[shift+2]) and \
                      money_pattern.match(raw_data[shift+3]) and \
                      money_pattern.match(raw_data[shift+5])): # quantity, proceeds, acquired_date, cost, ..., gain_loss
                    
                    shift += 1

                data_part = raw_data[shift:shift+6]
                print(data_part)

                idx = shift + 6
            
        else:
            # Single entry
            
            # description
            assert(date_pattern.match(raw_data[1])) # sold_date
            assert(quantity_pattern.match(raw_data[2])) # quantity
            assert(money_pattern.match(raw_data[3])) # proceeds
            assert(date_pattern.match(raw_data[4])) # acquired_date
            assert(money_pattern.match(raw_data[5])) # cost
            # wash_sales_loss
            assert(money_pattern.match(raw_data[7])) # gain_loss

            filtered = raw_data[0:8]
            print(filtered)

            pass


    def to_csv():
        pass
