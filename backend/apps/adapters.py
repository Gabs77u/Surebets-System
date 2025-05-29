"""
Sistema unificado de adaptadores de bookmaker para o Surebets Hunter Pro.

Consolida as implementações duplicadas e padroniza a interface para todas
as casas de apostas, removendo redundâncias entre diferentes adapters.
"""

from typing import Any, Dict, List, Optional, Union
import logging
import os
import json
import random
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

# Configurar logging
logger = logging.getLogger(__name__)

class UnifiedBookmakerAdapter(ABC):
    """
    Adaptador base unificado para todas as casas de apostas.
    
    Esta classe consolida funcionalidades comuns e remove redundâncias
    entre diferentes implementações de adaptadores.
    """
    
    def __init__(self, bookmaker_name: str, bookmaker_id: int):
        self.bookmaker_name = bookmaker_name
        self.bookmaker_id = bookmaker_id
        self.is_mock_mode = os.getenv('MOCK_BOOKMAKER_DATA', 'true').lower() == 'true'
        
        # Configurações base comuns a todos os bookmakers
        self.base_settings = {
            'timeout': int(os.getenv('BOOKMAKER_TIMEOUT', '30')),
            'max_retries': int(os.getenv('BOOKMAKER_MAX_RETRIES', '3')),
            'rate_limit': float(os.getenv('BOOKMAKER_RATE_LIMIT', '1.0')),
            'min_odds': float(os.getenv('GLOBAL_MIN_ODDS', '1.01')),
            'max_odds': float(os.getenv('GLOBAL_MAX_ODDS', '1000')),
        }
        
        # Configurações específicas do bookmaker (sobrescritas pelas subclasses)
        self.custom_settings = {}
        
        logger.info(f"Inicializando adaptador unificado para {bookmaker_name}")
        if self.is_mock_mode:
            logger.warning(f"Modo MOCK ativado para {bookmaker_name}")
    
    @abstractmethod
    def get_custom_settings(self) -> Dict[str, Any]:
        """
        Retorna configurações específicas do bookmaker.
        Deve ser implementado pelas subclasses.
        """
        pass
    
    def get_effective_settings(self) -> Dict[str, Any]:
        """
        Retorna as configurações efetivas (base + custom).
        """
        settings = self.base_settings.copy()
        settings.update(self.get_custom_settings())
        return settings
    
    def get_live_odds(self, sport: str = "soccer", limit: int = 50) -> List[Dict[str, Any]]:
        """
        Busca odds ao vivo unificadas.
        """
        if self.is_mock_mode:
            return self._generate_mock_live_odds(sport, limit)
        
        return self._fetch_real_live_odds(sport, limit)
    
    def get_upcoming_odds(self, sport: str = "soccer", limit: int = 50) -> List[Dict[str, Any]]:
        """
        Busca odds de eventos futuros unificadas.
        """
        if self.is_mock_mode:
            return self._generate_mock_upcoming_odds(sport, limit)
        
        return self._fetch_real_upcoming_odds(sport, limit)
    
    def get_markets(self, event_id: str) -> List[Dict[str, Any]]:
        """
        Busca mercados para um evento específico.
        """
        if self.is_mock_mode:
            return self._generate_mock_markets(event_id)
        
        return self._fetch_real_markets(event_id)
    
    def _generate_mock_live_odds(self, sport: str, limit: int) -> List[Dict[str, Any]]:
        """
        Gera dados mock unificados para odds ao vivo.
        Centraliza a lógica de mock para evitar duplicação.
        """
        mock_events = []
        
        # Templates de eventos baseados no esporte
        event_templates = self._get_sport_templates(sport)
        
        for i in range(min(limit, len(event_templates))):
            template = event_templates[i]
            
            # Gera odds realistas baseadas no bookmaker
            odds_multiplier = self._get_bookmaker_odds_multiplier()
            
            event = {
                'id': f"{self.bookmaker_name}_{sport}_{i + 1}",
                'name': template['name'],
                'sport': sport,
                'status': 'live',
                'start_time': (datetime.now() - timedelta(minutes=random.randint(1, 90))).isoformat(),
                'bookmaker': self.bookmaker_name,
                'markets': [
                    {
                        'type': '1X2',
                        'name': 'Resultado Final',
                        'selections': [
                            {
                                'name': template['home'],
                                'odds': round(random.uniform(1.5, 4.0) * odds_multiplier, 2)
                            },
                            {
                                'name': 'Empate',
                                'odds': round(random.uniform(2.8, 3.8) * odds_multiplier, 2)
                            },
                            {
                                'name': template['away'],
                                'odds': round(random.uniform(1.5, 4.0) * odds_multiplier, 2)
                            }
                        ]
                    }
                ]
            }
            
            mock_events.append(event)
        
        return mock_events
    
    def _generate_mock_upcoming_odds(self, sport: str, limit: int) -> List[Dict[str, Any]]:
        """
        Gera dados mock unificados para odds de eventos futuros.
        """
        mock_events = []
        event_templates = self._get_sport_templates(sport)
        
        for i in range(min(limit, len(event_templates))):
            template = event_templates[i]
            odds_multiplier = self._get_bookmaker_odds_multiplier()
            
            event = {
                'id': f"{self.bookmaker_name}_{sport}_upcoming_{i + 1}",
                'name': template['name'],
                'sport': sport,
                'status': 'upcoming',
                'start_time': (datetime.now() + timedelta(hours=random.randint(1, 72))).isoformat(),
                'bookmaker': self.bookmaker_name,
                'markets': [
                    {
                        'type': '1X2',
                        'name': 'Resultado Final',
                        'selections': [
                            {
                                'name': template['home'],
                                'odds': round(random.uniform(1.3, 5.0) * odds_multiplier, 2)
                            },
                            {
                                'name': 'Empate',
                                'odds': round(random.uniform(2.5, 4.2) * odds_multiplier, 2)
                            },
                            {
                                'name': template['away'],
                                'odds': round(random.uniform(1.3, 5.0) * odds_multiplier, 2)
                            }
                        ]
                    }
                ]
            }
            
            mock_events.append(event)
        
        return mock_events
    
    def _generate_mock_markets(self, event_id: str) -> List[Dict[str, Any]]:
        """
        Gera mercados mock para um evento específico.
        """
        odds_multiplier = self._get_bookmaker_odds_multiplier()
        
        return [
            {
                'type': '1X2',
                'name': 'Resultado Final',
                'selections': [
                    {'name': 'Casa', 'odds': round(random.uniform(1.5, 3.0) * odds_multiplier, 2)},
                    {'name': 'Empate', 'odds': round(random.uniform(2.8, 3.8) * odds_multiplier, 2)},
                    {'name': 'Visitante', 'odds': round(random.uniform(1.5, 3.0) * odds_multiplier, 2)}
                ]
            },
            {
                'type': 'OU',
                'name': 'Total de Gols',
                'selections': [
                    {'name': 'Mais de 2.5', 'odds': round(random.uniform(1.6, 2.2) * odds_multiplier, 2)},
                    {'name': 'Menos de 2.5', 'odds': round(random.uniform(1.6, 2.2) * odds_multiplier, 2)}
                ]
            },
            {
                'type': 'DC',
                'name': 'Dupla Chance',
                'selections': [
                    {'name': '1X', 'odds': round(random.uniform(1.2, 1.8) * odds_multiplier, 2)},
                    {'name': '12', 'odds': round(random.uniform(1.1, 1.4) * odds_multiplier, 2)},
                    {'name': 'X2', 'odds': round(random.uniform(1.2, 1.8) * odds_multiplier, 2)}
                ]
            }
        ]
    
    def _get_sport_templates(self, sport: str) -> List[Dict[str, str]]:
        """
        Retorna templates de eventos baseados no esporte.
        Centraliza os dados mock para evitar duplicação.
        """
        templates = {
            'soccer': [
                {'name': 'Real Madrid vs Barcelona', 'home': 'Real Madrid', 'away': 'Barcelona'},
                {'name': 'Manchester United vs Liverpool', 'home': 'Manchester United', 'away': 'Liverpool'},
                {'name': 'Bayern Munich vs Borussia Dortmund', 'home': 'Bayern Munich', 'away': 'Borussia Dortmund'},
                {'name': 'PSG vs Marseille', 'home': 'PSG', 'away': 'Marseille'},
                {'name': 'Flamengo vs Palmeiras', 'home': 'Flamengo', 'away': 'Palmeiras'},
                {'name': 'Santos vs Corinthians', 'home': 'Santos', 'away': 'Corinthians'},
                {'name': 'Inter vs Milan', 'home': 'Inter', 'away': 'Milan'},
                {'name': 'Arsenal vs Chelsea', 'home': 'Arsenal', 'away': 'Chelsea'},
            ],
            'tennis': [
                {'name': 'Djokovic vs Nadal', 'home': 'Djokovic', 'away': 'Nadal'},
                {'name': 'Federer vs Murray', 'home': 'Federer', 'away': 'Murray'},
                {'name': 'Serena Williams vs Sharapova', 'home': 'Serena Williams', 'away': 'Sharapova'},
                {'name': 'Tsitsipas vs Zverev', 'home': 'Tsitsipas', 'away': 'Zverev'},
            ],
            'basketball': [
                {'name': 'Lakers vs Warriors', 'home': 'Lakers', 'away': 'Warriors'},
                {'name': 'Celtics vs Heat', 'home': 'Celtics', 'away': 'Heat'},
                {'name': 'Bulls vs Knicks', 'home': 'Bulls', 'away': 'Knicks'},
                {'name': 'Spurs vs Rockets', 'home': 'Spurs', 'away': 'Rockets'},
            ]
        }
        
        return templates.get(sport, templates['soccer'])
    
    def _get_bookmaker_odds_multiplier(self) -> float:
        """
        Retorna multiplicador de odds específico do bookmaker.
        Permite simular diferenças entre casas de apostas.
        """
        multipliers = {
            'bet365': 1.0,      # Odds padrão
            'pinnacle': 1.05,   # Odds ligeiramente melhores
            'betfair': 1.02,    # Odds de exchange
            'superodds': 0.98   # Odds ligeiramente piores
        }
        
        return multipliers.get(self.bookmaker_name, 1.0)
    
    def _fetch_real_live_odds(self, sport: str, limit: int) -> List[Dict[str, Any]]:
        """
        Busca odds reais ao vivo.
        Deve ser implementado pelas subclasses para integração real.
        """
        logger.warning(f"Integração real não implementada para {self.bookmaker_name}")
        return []
    
    def _fetch_real_upcoming_odds(self, sport: str, limit: int) -> List[Dict[str, Any]]:
        """
        Busca odds reais de eventos futuros.
        Deve ser implementado pelas subclasses para integração real.
        """
        logger.warning(f"Integração real não implementada para {self.bookmaker_name}")
        return []
    
    def _fetch_real_markets(self, event_id: str) -> List[Dict[str, Any]]:
        """
        Busca mercados reais para um evento.
        Deve ser implementado pelas subclasses para integração real.
        """
        logger.warning(f"Integração real não implementada para {self.bookmaker_name}")
        return []
    
    def get_name(self) -> str:
        """Retorna o nome do bookmaker."""
        return self.bookmaker_name
    
    def get_id(self) -> int:
        """Retorna o ID do bookmaker."""
        return self.bookmaker_id


# Implementações específicas para cada bookmaker
class Bet365UnifiedAdapter(UnifiedBookmakerAdapter):
    """Adaptador unificado para Bet365."""
    
    def __init__(self):
        super().__init__("bet365", 1)
    
    def get_custom_settings(self) -> Dict[str, Any]:
        return {
            'min_odds': float(os.getenv("BET365_MIN_ODDS", "1.01")),
            'max_odds': float(os.getenv("BET365_MAX_ODDS", "1000")),
            'filter_inplay': os.getenv("BET365_FILTER_INPLAY", "true").lower() == "true"
        }


class PinnacleUnifiedAdapter(UnifiedBookmakerAdapter):
    """Adaptador unificado para Pinnacle."""
    
    def __init__(self):
        super().__init__("pinnacle", 2)
    
    def get_custom_settings(self) -> Dict[str, Any]:
        return {
            'min_odds': float(os.getenv("PINNACLE_MIN_ODDS", "1.01")),
            'max_odds': float(os.getenv("PINNACLE_MAX_ODDS", "2000")),
            'asian_handicap': os.getenv("PINNACLE_ASIAN_HANDICAP", "true").lower() == "true",
            'market_types': os.getenv("PINNACLE_MARKET_TYPES", "1_1,1_2,1_3").split(",")
        }


class BetfairUnifiedAdapter(UnifiedBookmakerAdapter):
    """Adaptador unificado para Betfair."""
    
    def __init__(self):
        super().__init__("betfair", 3)
    
    def get_custom_settings(self) -> Dict[str, Any]:
        return {
            'min_odds': float(os.getenv("BETFAIR_MIN_ODDS", "1.01")),
            'max_odds': float(os.getenv("BETFAIR_MAX_ODDS", "1000")),
            'exchange_mode': os.getenv("BETFAIR_EXCHANGE_MODE", "true").lower() == "true",
            'commission_rate': float(os.getenv("BETFAIR_COMMISSION", "0.05"))
        }


class SuperOddsUnifiedAdapter(UnifiedBookmakerAdapter):
    """Adaptador unificado para Super Odds."""
    
    def __init__(self):
        super().__init__("superodds", 4)
    
    def get_custom_settings(self) -> Dict[str, Any]:
        return {
            'min_odds': float(os.getenv("SUPERODDS_MIN_ODDS", "1.01")),
            'max_odds': float(os.getenv("SUPERODDS_MAX_ODDS", "500")),
            'bonus_markets': os.getenv("SUPERODDS_BONUS_MARKETS", "true").lower() == "true"
        }


# Registry unificado de adaptadores
UNIFIED_BOOKMAKER_ADAPTERS = {
    'bet365': Bet365UnifiedAdapter(),
    'pinnacle': PinnacleUnifiedAdapter(),
    'betfair': BetfairUnifiedAdapter(),
    'superodds': SuperOddsUnifiedAdapter(),
}

def get_adapter(bookmaker_name: str) -> Optional[UnifiedBookmakerAdapter]:
    """
    Retorna o adaptador para um bookmaker específico.
    
    Args:
        bookmaker_name: Nome do bookmaker
        
    Returns:
        Adaptador unificado ou None se não encontrado
    """
    return UNIFIED_BOOKMAKER_ADAPTERS.get(bookmaker_name.lower())

def get_all_adapters() -> Dict[str, UnifiedBookmakerAdapter]:
    """
    Retorna todos os adaptadores disponíveis.
    
    Returns:
        Dicionário com todos os adaptadores
    """
    return UNIFIED_BOOKMAKER_ADAPTERS.copy()

def get_bookmaker_names() -> List[str]:
    """
    Retorna lista com nomes de todos os bookmakers disponíveis.
    
    Returns:
        Lista de nomes dos bookmakers
    """
    return list(UNIFIED_BOOKMAKER_ADAPTERS.keys())
