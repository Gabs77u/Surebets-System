from typing import List, Dict, Any
import itertools

class SurebetDetector:
    """
    Algoritmo para detecção de arbitragem (surebets).
    Recebe odds de diferentes casas, agrupa por evento e mercado, e identifica oportunidades de arbitragem.
    """

    @staticmethod
    def calculate_arbitrage(odds: List[float]) -> float:
        """Calcula o índice de arbitragem. Se < 1, há surebet."""
        return sum(1/o for o in odds if o > 0)

    @staticmethod
    def find_surebets(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Recebe uma lista de eventos, cada um com odds de diferentes casas e seleções.
        Retorna oportunidades de surebet encontradas.
        events: [
            {
                'event_id': str,
                'market': str,
                'selections': [
                    {'name': str, 'odds': float, 'bookmaker': str},
                    ...
                ]
            },
            ...
        ]
        """
        surebets = []
        for event in events:
            selections = event['selections']
            # Agrupa seleções por nome (ex: Home, Draw, Away)
            selection_names = list({s['name'] for s in selections})
            # Gera todas as combinações possíveis, uma odd por seleção, de casas diferentes
            combos = list(itertools.product(*[
                [s for s in selections if s['name'] == sel] for sel in selection_names
            ]))
            for combo in combos:
                # Garante que cada odd vem de uma casa diferente
                bookmakers = [s['bookmaker'] for s in combo]
                if len(set(bookmakers)) != len(bookmakers):
                    continue
                odds = [s['odds'] for s in combo]
                arb_index = SurebetDetector.calculate_arbitrage(odds)
                if arb_index < 1:
                    profit_percent = (1-arb_index)*100
                    surebets.append({
                        'event_id': event['event_id'],
                        'market': event['market'],
                        'selections': combo,
                        'arbitrage_index': arb_index,
                        'profit_percent': profit_percent
                    })
        return surebets
