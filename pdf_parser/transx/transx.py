import re
import locale
import io, csv


class Transx:

    columns = ["description", "sold_date", "quantity", "proceeds", "acquired_date", "cost", "wash_sales_loss", "gain_loss"]

    _comma_number_pat = "\d?\d?\d(,\d\d\d)*"
    _date_pat = "\d\d\/\d\d\/\d\d"

    _date_pattern = re.compile(f"^{_date_pat}$")
    _quantity_pattern = re.compile(f"^{_comma_number_pat}\.\d+$")
    _money_pattern = re.compile(f"^\-?{_comma_number_pat}\.\d\d$")


    def __init__(self, data):
        assert(isinstance(data, list))
        assert(len(data) == 8)
        # == Columns ==
        assert(isinstance(data[0], str)) # descripion
        assert(Transx._date_pattern.match(data[1])) # sold_date
        assert(Transx._quantity_pattern.match(data[2])) # quantity
        assert(re.match(f"^\-?{self._comma_number_pat}\.\d\d( [NG])?$", data[3])) # proceeds
        assert(Transx._date_pattern.match(data[4])) # acquired_date
        assert(Transx._money_pattern.match(data[5])) # cost
        assert(re.match(f"^(\-?{self._comma_number_pat}\.\d\d [W])?$", data[6])) # wash_sales_loss
        assert(Transx._money_pattern.match(data[7])) # gain_loss
        self.data = data

    
    def get_proceeds(self):
        val = self.data[3].split()[0]
        match = self._money_pattern.match(val)
        return float(match.group().replace(',',''))


    def get_cost(self):
        match = self._money_pattern.match(self.data[5])
        return float(match.group().replace(',',''))

    
    def get_wash_sales_loss(self):
        if not self.data[6]:
            return 0.
        val = self.data[6].split()[0]
        match = self._money_pattern.match(val)
        return float(match.group().replace(',',''))

    
    def get_gain_loss(self):
        match = self._money_pattern.match(self.data[7])
        return float(match.group().replace(',',''))


    @staticmethod
    def parse(raw_data: list) -> list:
        transx = []
        assert(isinstance(raw_data, list))

        desc = raw_data[0].strip()

        shift = 1
        while shift < len(raw_data) - 7:
            if multi := re.match(f"^(?P<cnt>{Transx._comma_number_pat}) transactions for (?P<sold_date>{Transx._date_pat}).", raw_data[shift]):
                # Multiple entries
                cnt = locale.atoi(multi.group("cnt"))
                sold_date = multi.group("sold_date")

                # print(f"{cnt} transactions sold on {sold_date}")
            elif Transx._date_pattern.match(raw_data[shift]):
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
                if not Transx._quantity_pattern.match(raw_data[shift+shift_extra]):
                    if cnt > 1: continue
                    else: break
                filtered.append(raw_data[shift+shift_extra])

                # proceeds
                if not Transx._money_pattern.match(raw_data[shift+shift_extra+1]):
                    if cnt > 1: continue
                    else: break
                filtered.append(raw_data[shift+shift_extra+1])
                # Gross Net - Potential Extra character
                gross_net = raw_data[shift+shift_extra+2]
                if gross_net == 'N' or gross_net == 'G':
                    filtered[1] += " " + gross_net
                    shift_extra += 1

                # date_acquired
                if not Transx._date_pattern.match(raw_data[shift+shift_extra+2]):
                    if cnt > 1: continue
                    else: break
                filtered.append(raw_data[shift+shift_extra+2])

                # cost
                if not Transx._money_pattern.match(raw_data[shift+shift_extra+3]): 
                    if cnt > 1: continue
                    else: break
                filtered.append(raw_data[shift+shift_extra+3])

                # wash_sales_loss
                if raw_data[shift+shift_extra+4] == "...":
                    filtered.append("")

                elif Transx._money_pattern.match(raw_data[shift+shift_extra+4]):
                    filtered.append(raw_data[shift+shift_extra+4])
                    # disallowed - Potential Extra character
                    if raw_data[shift+shift_extra+5] == "W":
                        filtered[4] += " " + raw_data[shift+shift_extra+5]
                        shift_extra += 1

                else:
                    if cnt > 1: continue
                    else: break
                
                # gain_loss
                if not Transx._money_pattern.match(raw_data[shift+shift_extra+5]):
                    if cnt > 1: continue
                    else: break
                filtered.append(raw_data[shift+shift_extra+5])
                
                if cnt > 1:
                    # Count check
                    raw_nth = raw_data[shift+shift_extra+6]
                    assert(nth_data := re.match(f"^(?P<nth>{Transx._comma_number_pat}) of (?P<total>{Transx._comma_number_pat})$", raw_nth))
                    assert(locale.atoi(nth_data.group("nth")) == n + 1)
                    assert(locale.atoi(nth_data.group("total")) == cnt)
                
                # Add sold_date to the front
                filtered.insert(0, sold_date)
                filtered.insert(0, desc)
                transx.append(Transx(filtered))
                # print(filtered)

                shift += shift_extra + 6
                n += 1
                # Clean
                del filtered

        return transx


    def write_csv(self, csv_writer):
        # output = io.StringIO()
        # writer = csv.writer(output)
        csv_writer.writerow(self.data)
        # return output.getvalue()
