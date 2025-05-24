from flask import Blueprint, jsonify, request
from backend.api_integrations import BOOKMAKER_ADAPTERS

bp = Blueprint('games_api', __name__)

@bp.route('/api/games/live', methods=['GET'])
def get_live_games():
    """Busca jogos ao vivo de todas as plataformas integradas."""
    results = []
    for name, adapter in BOOKMAKER_ADAPTERS.items():
        try:
            # Supondo que cada adapter tenha um método get_live_games()
            games = adapter.get_live_games() if hasattr(adapter, 'get_live_games') else []
            for g in games:
                g['bookmaker'] = name
            results.extend(games)
        except Exception as e:
            continue
    return jsonify({'games': results})

@bp.route('/api/games/upcoming', methods=['GET'])
def get_upcoming_games():
    """Busca jogos futuros/próximos de todas as plataformas integradas."""
    results = []
    for name, adapter in BOOKMAKER_ADAPTERS.items():
        try:
            # Supondo que cada adapter tenha um método get_upcoming_games()
            games = adapter.get_upcoming_games() if hasattr(adapter, 'get_upcoming_games') else []
            for g in games:
                g['bookmaker'] = name
            results.extend(games)
        except Exception as e:
            continue
    return jsonify({'games': results})

@bp.route('/api/games/search', methods=['GET'])
def search_games():
    """Busca jogos por termo (nome/time) em todas as plataformas."""
    query = request.args.get('q', '')
    results = []
    for name, adapter in BOOKMAKER_ADAPTERS.items():
        try:
            # Supondo que cada adapter tenha um método search_events(query)
            games = adapter.search_events(query) if hasattr(adapter, 'search_events') else []
            for g in games:
                g['bookmaker'] = name
            results.extend(games)
        except Exception as e:
            continue
    return jsonify({'games': results})
