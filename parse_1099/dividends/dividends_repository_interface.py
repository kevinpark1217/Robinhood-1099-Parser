from typing import Union
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from pandas.core.series import Series

class By():
    CUSIP = 1
    SYMBOL = 2

class DividendsRepositoryInterface:

    def get_dividend_exdates(self, by: Literal[int], lookup: Union[str, "list[str]"], tax_year: int) -> "tuple[Union[Series, None], dict[str, str]]": #type:ignore
        pass
