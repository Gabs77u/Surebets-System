from .bookmaker_adapter_base import BookmakerAdapterBase
from typing import Any, Dict

class SuperOddsAdapter(BookmakerAdapterBase):
    """Adapter para integração com a API da Super Odds."""

    def get_odds(self, event_id: str) -> Dict[str, Any]:
        # Implementação mock
        return {
            "event_id": event_id,
            "odds": {
                "home": 2.10,
                "draw": 3.50,
                "away": 3.60
            }
        }

    def search_events(self, query: str) -> Any:
        # Implementação mock
        return [
            {"event_id": "401", "name": "Super Time x Mega Time"},
            {"event_id": "402", "name": "Ultra Time x Hyper Time"}
        ]
