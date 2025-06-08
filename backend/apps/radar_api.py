import requests
from typing import Any, Dict, Optional

# [UTILITÁRIO INTERNO] Este módulo deve ser usado apenas via backend/apps/integration.py.
# Não expor diretamente para endpoints ou outros módulos.


class SportRadarAPI:
    def __init__(self, betting_house: str):
        self.betting_house = betting_house
        self.base_url = "https://s5.sir.sportradar.com/"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "accept": "application/json, text/plain, */*",
                "user-agent": "Mozilla/5.0 (compatible; SurebetsSystem/1.0)",
            }
        )

    def all_definitions(
        self, id: str = "5bc333c9e86aeb31125b4b35e9038eb5"
    ) -> Optional[Dict[str, Any]]:
        url = f"https://s5.sir.sportradar.com/translations/common/en.{id}.json"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def modal_data(
        self, sport_id: str, method: str = "all"
    ) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}{self.betting_house}/en/Europe:Berlin/gismo/config_tree_mini/41/0/{sport_id}"
        resp = self.session.get(url)
        # Log da resposta bruta para debug
        try:
            logger = __import__("logging").getLogger(__name__)
            logger.debug(
                f"[SportRadarAPI] URL: {url} | Status: {resp.status_code} | Conteúdo: {resp.text[:500]}"
            )
        except Exception as log_exc:
            pass
        resp.raise_for_status()
        data = resp.json()
        if method == "all":
            return data
        if method == "categories":
            return data["doc"][0]["data"][0]
        return None

    def local_data(
        self, sport_id: str, local_id: str, method: str = "all"
    ) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}{self.betting_house}/en/Europe:Berlin/gismo/config_tree_mini/41/0/{sport_id}/{local_id}"
        resp = self.session.get(url)
        # Log da resposta bruta para debug
        try:
            logger = __import__("logging").getLogger(__name__)
            logger.debug(
                f"[SportRadarAPI] URL: {url} | Status: {resp.status_code} | Conteúdo: {resp.text[:500]}"
            )
        except Exception as log_exc:
            pass
        resp.raise_for_status()
        if method == "all":
            return resp.json()
        return None

    def league(self, league_id: str) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}{self.betting_house}/en/America:Argentina:Buenos_Aires/gismo/stats_season_meta/{league_id}"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def league_summary(self, league_id: str) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}common/en/Europe:Berlin/gismo/stats_season_leaguesummary/{league_id}/main"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def season_goals(self, league_id: str) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}{self.betting_house}/en/America:Argentina:Buenos_Aires/gismo/stats_season_goals/{league_id}/main"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def league_fixtures(self, league_id: str) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}{self.betting_house}/en/America:Argentina:Buenos_Aires/gismo/stats_season_fixtures2/{league_id}/1"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def get_by_path(self, path: str) -> Optional[Dict[str, Any]]:
        # Corrige para sempre usar URL absoluta
        if path.startswith("http"):
            url = path
        else:
            url = f"{self.base_url}{path}"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def get_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        # Garante que a URL é absoluta
        if not url.startswith("http"):
            url = f"{self.base_url}{url}"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def get_info(
        self,
        region: str,
        method: str,
        values: str,
        configs: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        configs = configs or {}
        get_common = configs.get("getCommonContents", False)
        language_id = configs.get("languageId", "514d1e14ad5c11eeebf17ba7f5dc97ad")
        lang = configs.get("lang", "en")
        server = configs.get("server", "gismo")
        if get_common and method == "common":
            url = f"https://s5.sir.sportradar.com/translations/common/en.{language_id}.json"
            resp = self.session.get(url)
            resp.raise_for_status()
            return resp.json()
        else:
            url = f"{self.base_url}{self.betting_house}/{lang}/{region}/{server}/{method}/{values}"
            resp = self.session.get(url)
            resp.raise_for_status()
            return resp.json().get("doc", [{}])[0]

    def get_sports_ids(self) -> Optional[Dict[str, Any]]:
        """
        Busca a lista de esportes e seus IDs disponíveis na API.
        Tenta com e sem o prefixo da casa. Retorna None se ambos falharem.
        """
        urls = [
            f"{self.base_url}{self.betting_house}/en/Europe:Berlin/gismo/config_tree_mini/41/0",
            f"{self.base_url}en/Europe:Berlin/gismo/config_tree_mini/41/0",
        ]
        for url in urls:
            try:
                resp = self.session.get(url)
                resp.raise_for_status()
                data = resp.json()
                if data and "doc" in data:
                    return data
            except Exception as e:
                continue
        return None

    def modal_data_region(
        self, sport_id: str, region: str = "Europe:Berlin", method: str = "all"
    ) -> Optional[Dict[str, Any]]:
        """
        Busca dados do esporte para uma região específica.
        """
        url = f"{self.base_url}{self.betting_house}/en/{region}/gismo/config_tree_mini/41/0/{sport_id}"
        resp = self.session.get(url)
        resp.raise_for_status()
        data = resp.json()
        if method == "all":
            return data
        if method == "categories":
            return data["doc"][0]["data"][0]
        return None

    def local_data_region(
        self,
        sport_id: str,
        local_id: str,
        region: str = "Europe:Berlin",
        method: str = "all",
    ) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}{self.betting_house}/en/{region}/gismo/config_tree_mini/41/0/{sport_id}/{local_id}"
        resp = self.session.get(url)
        resp.raise_for_status()
        if method == "all":
            return resp.json()
        return None

    def league_region(
        self, league_id: str, region: str = "America:Argentina:Buenos_Aires"
    ) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}{self.betting_house}/en/{region}/gismo/stats_season_meta/{league_id}"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def league_fixtures_region(
        self, league_id: str, region: str = "America:Argentina:Buenos_Aires"
    ) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}{self.betting_house}/en/{region}/gismo/stats_season_fixtures2/{league_id}/1"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    # Estrutura para integração WebSocket (exemplo, implementação real depende do endpoint)
    def connect_websocket(
        self, ws_url: str, on_message=None, on_error=None, on_close=None
    ):
        """
        Conecta a um WebSocket e consome mensagens em tempo real.
        Exemplo de uso:
        api.connect_websocket('wss://exemplo.com/ws', on_message=print)
        """
        import websocket

        ws = websocket.WebSocketApp(
            ws_url, on_message=on_message, on_error=on_error, on_close=on_close
        )
        ws.run_forever()

    # Exemplo de uso correto:
    # 1. ids = api.get_sports_ids()
    # 2. Use ids['doc'][0]['data'] para encontrar o ID do esporte desejado (ex: futebol/soccer)
    # 3. Passe esse ID para os outros métodos (ex: modal_data(sport_id=1))
