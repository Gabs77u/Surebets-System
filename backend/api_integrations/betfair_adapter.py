from .bookmaker_adapter_base import BookmakerAdapterBase
from typing import Any, Dict

class BetfairAdapter(BookmakerAdapterBase):
    """Adapter para integração com a API da Betfair."""

    def get_odds(self, event_id: str) -> Dict[str, Any]:
        # Implementação mock
        return {
            "event_id": event_id,
            "odds": {
                "home": 2.00,
                "draw": 3.00,
                "away": 3.80
            }
        }

    def search_events(self, query: str) -> Any:
        # Implementação mock
        return [
            {"event_id": "301", "name": "Clube 1 x Clube 2"},
            {"event_id": "302", "name": "Clube 3 x Clube 4"}
        ]
