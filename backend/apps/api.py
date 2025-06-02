from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from backend.apps.radar_api import SportRadarAPI

app = Flask(__name__)
CORS(app)


class UnifiedBookmakerAPI:
    """
    API unificada para integração com múltiplas casas de apostas via SportRadarAPI.
    Centraliza configuração e expõe métodos padronizados para odds, ligas, fixtures, etc.
    """
    def __init__(self, bookmakers=None):
        # Configuração centralizada
        if bookmakers is None:
            bookmakers = [
                'bet365',
                'pinnacle',
                'betfair',
                'superodds'
            ]
        self.bookmakers = bookmakers
        self.instances = {
            house: SportRadarAPI(house)
            for house in self.bookmakers
        }

    def get_api(self, house):
        return self.instances.get(house)

    def get_all_apis(self):
        return self.instances

    def get_odds(self, house, sport_id, region=None, method='all'):
        api = self.get_api(house)
        if not api:
            return None
        if region:
            return api.modal_data_region(
                sport_id, region, method
            )
        return api.modal_data(sport_id, method)

    def get_league(self, house, league_id, region=None):
        api = self.get_api(house)
        if not api:
            return None
        if region:
            return api.league_region(
                league_id, region
            )
        return api.league(league_id)

    def get_fixtures(self, house, league_id, region=None):
        api = self.get_api(house)
        if not api:
            return None
        if region:
            return api.league_fixtures_region(
                league_id, region
            )
        return api.league_fixtures(league_id)

    def get_sports_ids(self, house):
        api = self.get_api(house)
        if not api:
            return None
        return api.get_sports_ids()


unified_api = UnifiedBookmakerAPI()


@app.route('/api/bookmakers', methods=['GET'])
def get_bookmakers():
    """Lista todas as casas de apostas disponíveis."""
    return jsonify({'bookmakers': unified_api.bookmakers})


@app.route('/api/odds', methods=['GET'])
def get_odds():
    """Retorna odds para um bookmaker e esporte."""
    house = request.args.get('bookmaker')
    sport_id = request.args.get('sport_id')
    region = request.args.get('region')
    method = request.args.get('method', 'all')
    if not house or not sport_id:
        return jsonify({'error': 'Parâmetros obrigatórios: bookmaker, sport_id'}), 400
    odds = unified_api.get_odds(house, sport_id, region, method)
    return jsonify({'odds': odds})


@app.route('/api/leagues', methods=['GET'])
def get_leagues():
    house = request.args.get('bookmaker')
    league_id = request.args.get('league_id')
    region = request.args.get('region')
    if not house or not league_id:
        return jsonify({'error': 'Parâmetros obrigatórios: bookmaker, league_id'}), 400
    league = unified_api.get_league(house, league_id, region)
    return jsonify({'league': league})


@app.route('/api/fixtures', methods=['GET'])
def get_fixtures():
    house = request.args.get('bookmaker')
    league_id = request.args.get('league_id')
    region = request.args.get('region')
    if not house or not league_id:
        return jsonify({'error': 'Parâmetros obrigatórios: bookmaker, league_id'}), 400
    fixtures = unified_api.get_fixtures(house, league_id, region)
    return jsonify({'fixtures': fixtures})


@app.route('/api/sports', methods=['GET'])
def get_sports():
    house = request.args.get('bookmaker')
    if not house:
        return jsonify({'error': 'Parâmetro obrigatório: bookmaker'}), 400
    sports = unified_api.get_sports_ids(house)
    return jsonify({'sports': sports})


@app.route('/api/status', methods=['GET'])
def api_status():
    return jsonify({
        'status': 'running',
        'version': '2.0.0-unified',
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'bookmakers': unified_api.bookmakers
    })


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('UNIFIED_API_PORT', 5050)),
        debug=False
    )
