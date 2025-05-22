from abc import ABC, abstractmethod
from typing import Any, Dict

class BookmakerAdapterBase(ABC):
    """Interface base para integração com APIs de Bookmakers."""

    @abstractmethod
    def get_odds(self, event_id: str) -> Dict[str, Any]:
        """Obtém odds para um evento específico."""
        pass

    @abstractmethod
    def search_events(self, query: str) -> Any:
        """Busca eventos na API da casa de aposta."""
        pass
