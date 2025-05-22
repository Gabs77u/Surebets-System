from .bet365_adapter import Bet365Adapter
from .pinnacle_adapter import PinnacleAdapter
from .betfair_adapter import BetfairAdapter
from .superodds_adapter import SuperOddsAdapter

BOOKMAKER_ADAPTERS = {
    'Bet365': Bet365Adapter(),
    'Pinnacle': PinnacleAdapter(),
    'Betfair': BetfairAdapter(),
    'Super Odds': SuperOddsAdapter(),
}
