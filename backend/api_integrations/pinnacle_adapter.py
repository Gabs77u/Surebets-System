import requests
from .bookmaker_adapter_base import BookmakerAdapterBase
from typing import Any, Dict, List

class PinnacleAdapter(BookmakerAdapterBase):
    """Adapter para integração com a API da Pinnacle (produção)."""

    # Preencha as credenciais abaixo quando disponíveis
    # API_KEY = "SUA_API_KEY_AQUI"
    # USERNAME = "SEU_USUARIO_AQUI"
    # PASSWORD = "SUA_SENHA_AQUI"
    BASE_URL = "https://api.pinnacle.com/v1/"  # Exemplo, ajuste conforme documentação oficial
    TIMEOUT = 10

    def get_odds(self, event_id: str) -> Dict[str, Any]:
        try:
            # url = f"{self.BASE_URL}events/{event_id}/odds"
            # headers = {"Authorization": f"Basic {self.API_KEY}"}
            # response = requests.get(url, headers=headers, timeout=self.TIMEOUT)
            # response.raise_for_status()
            # return response.json()
            # --- MOCK para desenvolvimento ---
            return {
                "event_id": event_id,
                "odds": {
                    "home": 1.90,
                    "draw": 3.10,
                    "away": 4.00
                }
            }
        except Exception as e:
            return {"error": str(e)}

    def search_events(self, query: str) -> List[Dict[str, Any]]:
        try:
            # url = f"{self.BASE_URL}events/search"
            # params = {"q": query}
            # headers = {"Authorization": f"Basic {self.API_KEY}"}
            # response = requests.get(url, headers=headers, params=params, timeout=self.TIMEOUT)
            # response.raise_for_status()
            # return response.json().get("results", [])
            # --- MOCK para desenvolvimento ---
            return [
                {"event_id": "201", "name": "Equipe X x Equipe Y"},
                {"event_id": "202", "name": "Equipe Z x Equipe W"}
            ]
        except Exception as e:
            return [{"error": str(e)}]

    def get_live_games(self) -> List[Dict[str, Any]]:
        try:
            # url = f"{self.BASE_URL}events/live"
            # headers = {"Authorization": f"Basic {self.API_KEY}"}
            # response = requests.get(url, headers=headers, timeout=self.TIMEOUT)
            # response.raise_for_status()
            # return response.json().get("games", [])
            # --- MOCK para desenvolvimento ---
            return [
                {"event_id": "PINN-LIVE-1", "name": "Equipe X x Equipe Y", "status": "live", "start_time": "2025-05-24T16:00:00"}
            ]
        except Exception as e:
            return [{"error": str(e)}]

    def get_upcoming_games(self) -> List[Dict[str, Any]]:
        try:
            # url = f"{self.BASE_URL}events/upcoming"
            # headers = {"Authorization": f"Basic {self.API_KEY}"}
            # response = requests.get(url, headers=headers, timeout=self.TIMEOUT)
            # response.raise_for_status()
            # return response.json().get("games", [])
            # --- MOCK para desenvolvimento ---
            return [
                {"event_id": "PINN-UP-1", "name": "Equipe Z x Equipe W", "status": "upcoming", "start_time": "2025-05-25T19:00:00"}
            ]
        except Exception as e:
            return [{"error": str(e)}]
