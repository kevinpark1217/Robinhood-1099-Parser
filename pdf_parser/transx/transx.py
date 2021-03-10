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

        shift = 1
        while shift < len(raw_data) - 7:
            if multi := re.match(f"^(?P<cnt>{comma_number_pat}) transactions for (?P<sold_date>{date_pat}).", raw_data[shift]):
                # Multiple entries
                cnt = locale.atoi(multi.group("cnt"))
                sold_date = multi.group("sold_date")

                print(f"{cnt} transactions sold on {sold_date}")
            elif date_pattern.match(raw_data[shift]):
                cnt = 1
                sold_date = raw_data[shift]
            else:
                shift += 1
                continue


            n = 0
            while n < cnt:
                shift += 1
                filtered = []
                shift_extra = 0

                # quantity
                if not quantity_pattern.match(raw_data[shift+shift_extra]):
                    if cnt > 1: continue
                    else: break
                filtered.append(raw_data[shift+shift_extra])

                # proceeds
                if not money_pattern.match(raw_data[shift+shift_extra+1]):
                    if cnt > 1: continue
                    else: break
                filtered.append(raw_data[shift+shift_extra+1])
                # Gross Net - Potential Extra character
                gross_net = raw_data[shift+shift_extra+2]
                if gross_net == 'N' or gross_net == 'G':
                    filtered[1] += " " + gross_net
                    shift_extra += 1

                # date_acquired
                if not date_pattern.match(raw_data[shift+shift_extra+2]):
                    if cnt > 1: continue
                    else: break
                filtered.append(raw_data[shift+shift_extra+2])

                # cost
                if not money_pattern.match(raw_data[shift+shift_extra+3]): 
                    if cnt > 1: continue
                    else: break
                filtered.append(raw_data[shift+shift_extra+3])

                # wash_sales_loss
                if raw_data[shift+shift_extra+4] == "...":
                    filtered.append("")

                elif money_pattern.match(raw_data[shift+shift_extra+4]):
                    filtered.append(raw_data[shift+shift_extra+4])
                    # disallowed - Potential Extra character
                    if raw_data[shift+shift_extra+5] == "W":
                        filtered[4] += " " + raw_data[shift+shift_extra+5]
                        shift_extra += 1

                else:
                    if cnt > 1: continue
                    else: break
                
                # gain_loss
                if not money_pattern.match(raw_data[shift+shift_extra+5]):
                    if cnt > 1: continue
                    else: break
                filtered.append(raw_data[shift+shift_extra+5])
                
                if cnt > 1:
                    # Count check
                    raw_nth = raw_data[shift+shift_extra+6]
                    assert(nth_data := re.match(f"^(?P<nth>{comma_number_pat}) of (?P<total>{comma_number_pat})$", raw_nth))
                    assert(locale.atoi(nth_data.group("nth")) == n + 1)
                    assert(locale.atoi(nth_data.group("total")) == cnt)
                
                # Add sold_date to the front
                filtered.insert(0, sold_date)
                print(filtered)

                shift += shift_extra + 6
                n += 1
                # Clean
                del filtered

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
