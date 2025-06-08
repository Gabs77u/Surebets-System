"""
Módulo unificado de integração para casas de apostas no Surebets System.
Centraliza toda a lógica de acesso real e mock, delegando para SportRadarAPI quando necessário.
"""

from typing import Any, Dict, List, Optional
import os
import logging
from datetime import datetime, timedelta
import random
from config.config_loader import CONFIG

logger = logging.getLogger(__name__)

class UnifiedBookmakerAdapter:
    def __init__(self, bookmaker_name: str):
        self.bookmaker_name = bookmaker_name
        self.is_mock_mode = os.getenv('MOCK_BOOKMAKER_DATA', str(CONFIG.get('mock_bookmaker_data', 'true'))).lower() == 'true'
        self.base_settings = {
            'timeout': int(os.getenv('BOOKMAKER_TIMEOUT', str(CONFIG.get('bookmaker_timeout', 30)))),
            'max_retries': int(os.getenv('BOOKMAKER_MAX_RETRIES', str(CONFIG.get('bookmaker_max_retries', 3)))),
            'rate_limit': float(os.getenv('BOOKMAKER_RATE_LIMIT', str(CONFIG.get('bookmaker_rate_limit', 1.0)))),
            'min_odds': float(os.getenv('GLOBAL_MIN_ODDS', str(CONFIG.get('global_min_odds', 1.01)))),
            'max_odds': float(os.getenv('GLOBAL_MAX_ODDS', str(CONFIG.get('global_max_odds', 1000)))),
        }
        logger.info(f"Inicializando adaptador unificado para {bookmaker_name}")
        if self.is_mock_mode:
            logger.warning(f"Modo MOCK ativado para {bookmaker_name}")

    def get_effective_settings(self) -> Dict[str, Any]:
        return self.base_settings.copy()

    def get_live_odds(self, sport: str = "soccer", limit: int = 50) -> List[Dict[str, Any]]:
        if self.is_mock_mode:
            return self._generate_mock_live_odds(sport, limit)
        # Exemplo: usar self.sportradar.modal_data(sport_id, ...)
        return self.sportradar.modal_data(sport, method='all')

    def get_upcoming_odds(self, sport: str = "soccer", limit: int = 50) -> List[Dict[str, Any]]:
        if self.is_mock_mode:
            return self._generate_mock_upcoming_odds(sport, limit)
        return self.sportradar.modal_data(sport, method='all')

    def get_markets(self, event_id: str) -> List[Dict[str, Any]]:
        if self.is_mock_mode:
            return self._generate_mock_markets(event_id)
        return self.sportradar.league(event_id)

    def get_league(self, league_id: str) -> Optional[Dict[str, Any]]:
        return self.sportradar.league(league_id)

    def get_fixtures(self, league_id: str) -> Optional[Dict[str, Any]]:
        return self.sportradar.league_fixtures(league_id)

    # Métodos mock simplificados
    def _generate_mock_live_odds(self, sport: str, limit: int) -> List[Dict[str, Any]]:
        return [{
            'id': f"mock_{sport}_{i}",
            'name': f"Mock Event {i}",
            'sport': sport,
            'status': 'live',
            'start_time': (datetime.now() - timedelta(minutes=random.randint(1, 90))).isoformat(),
            'odds': round(random.uniform(1.01, 10.0), 2)
        } for i in range(limit)]

    def _generate_mock_upcoming_odds(self, sport: str, limit: int) -> List[Dict[str, Any]]:
        return [{
            'id': f"mock_{sport}_upcoming_{i}",
            'name': f"Mock Upcoming {i}",
            'sport': sport,
            'status': 'upcoming',
            'start_time': (datetime.now() + timedelta(minutes=random.randint(10, 120))).isoformat(),
            'odds': round(random.uniform(1.01, 10.0), 2)
        } for i in range(limit)]

    def _generate_mock_markets(self, event_id: str) -> List[Dict[str, Any]]:
        return [{
            'market_id': f"mock_market_{event_id}_{i}",
            'name': f"Mock Market {i}",
            'selections': [
                {'name': 'A', 'odds': round(random.uniform(1.01, 5.0), 2)},
                {'name': 'B', 'odds': round(random.uniform(1.01, 5.0), 2)}
            ]
        } for i in range(3)]

# Factory para múltiplos bookmakers
class BookmakerIntegration:
    def __init__(self, bookmakers=None):
        if bookmakers is None:
            bookmakers = ['bet365', 'pinnacle', 'betfair', 'superodds']
        self.adapters = {name: UnifiedBookmakerAdapter(name) for name in bookmakers}

    def get_adapter(self, name: str) -> UnifiedBookmakerAdapter:
        return self.adapters[name]

    def list_bookmakers(self) -> List[str]:
        return list(self.adapters.keys())
