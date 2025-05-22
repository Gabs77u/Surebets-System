from .bet365 import Bet365
from .pinnacle import Pinnacle
from .betfair import Betfair
from .superodds import SuperOdds

BOOKMAKERS_LIST = [
    Bet365.get_info(),
    Pinnacle.get_info(),
    Betfair.get_info(),
    SuperOdds.get_info()
]
