from .bookmaker_adapter_base import BookmakerAdapterBase
from typing import Any, Dict

class PinnacleAdapter(BookmakerAdapterBase):
    """Adapter para integração com a API da Pinnacle."""

    def get_odds(self, event_id: str) -> Dict[str, Any]:
        # Implementação mock
        return {
            "event_id": event_id,
            "odds": {
                "home": 1.90,
                "draw": 3.10,
                "away": 4.00
            }
        }

    def search_events(self, query: str) -> Any:
        # Implementação mock
        return [
            {"event_id": "201", "name": "Equipe X x Equipe Y"},
            {"event_id": "202", "name": "Equipe Z x Equipe W"}
        ]
