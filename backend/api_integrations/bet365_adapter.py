from .bookmaker_adapter_base import BookmakerAdapterBase
from typing import Any, Dict

class Bet365Adapter(BookmakerAdapterBase):
    """Adapter para integração com a API da Bet365."""

    def get_odds(self, event_id: str) -> Dict[str, Any]:
        # Aqui você implementaria a chamada real à API da Bet365
        # Exemplo mock:
        return {
            "event_id": event_id,
            "odds": {
                "home": 1.85,
                "draw": 3.20,
                "away": 4.10
            }
        }

    def search_events(self, query: str) -> Any:
        # Aqui você implementaria a busca real na API da Bet365
        # Exemplo mock:
        return [
            {"event_id": "123", "name": "Time A x Time B"},
            {"event_id": "124", "name": "Time C x Time D"}
        ]
