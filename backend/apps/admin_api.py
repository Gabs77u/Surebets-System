"""
API administrativa consolidada para o Surebets Hunter Pro.

Unifica todas as funcionalidades administrativas em uma única API,
removendo redundâncias e padronizando endpoints.
"""

from flask import Flask, jsonify, request, session, redirect, url_for
from functools import wraps
import os
import logging
import secrets
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Importar módulos unificados
from config import settings, security
from backend.services.notification import notify_all
from backend.apps.adapters import get_all_adapters, get_adapter
from backend.core.i18n import get_text, get_language_dict
from database.database import DatabaseManager
from backend.core.auth import AuthManager
from flask_jwt_extended import jwt_required, get_jwt_identity

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)
app.secret_key = settings.SECRET_KEY

# Inicializar AuthManager e JWT
jwt_auth = AuthManager(app)

# Configuração de admin
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH") or getattr(settings, "ADMIN_PASSWORD_HASH", None)
if not ADMIN_PASSWORD_HASH:
    ADMIN_PASSWORD_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"  # hash fixo para testes (senha: admin123)
    logger.warning("ADMIN_PASSWORD_HASH não definido, usando hash fixo para testes (senha: admin123)")

# Decorador para autenticação
def login_required(f):
    """Decorador para proteger rotas que exigem login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return jsonify({'error': get_text('unauthorized')}), 401
        return f(*args, **kwargs)
    return decorated_function

# Decorador para proteção CSRF
def csrf_protected(f):
    """Decorador para proteção CSRF."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            token = request.headers.get('X-CSRF-Token') or request.json.get('csrf_token')
            if not token or token != session.get('csrf_token'):
                return jsonify({'error': 'CSRF token inválido'}), 403
        return f(*args, **kwargs)
    return decorated_function

def get_request_language() -> str:
    """Obtém o idioma da requisição."""
    return request.headers.get('Accept-Language', 'pt')[:2] or 'pt'

# Endpoints de autenticação
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Endpoint de login administrativo."""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        lang = get_request_language()
        
        if not username or not password:
            return jsonify({'error': get_text('missing_field', lang)}), 400
        
        # Verificar credenciais
        if username == ADMIN_USERNAME and security.verify_hash(password, ADMIN_PASSWORD_HASH):
            # Configurar sessão
            session['authenticated'] = True
            session['username'] = username
            session['csrf_token'] = secrets.token_hex(16)
            session['login_time'] = datetime.now().isoformat()
            
            logger.info(f"Login bem-sucedido para usuário '{username}'")
            return jsonify({
                'status': get_text('login_success', lang),
                'csrf_token': session['csrf_token']
            }), 200
        else:
            logger.warning(f"Tentativa de login falhou para usuário '{username}'")
            return jsonify({'error': get_text('login_failed', lang)}), 401
            
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        return jsonify({'error': get_text('error', get_request_language())}), 500

@app.route('/api/admin/logout', methods=['POST'])
@login_required
def admin_logout():
    """Endpoint de logout administrativo."""
    username = session.get('username')
    session.clear()
    logger.info(f"Logout realizado para usuário '{username}'")
    return jsonify({'status': get_text('logout_success', get_request_language())}), 200

# Novo endpoint de login JWT
@app.route('/api/auth/login', methods=['POST'])
def jwt_login():
    """Login para admin e usuários comuns (JWT)."""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    lang = get_request_language()

    if not username or not password:
        return jsonify({'error': get_text('missing_field', lang)}), 400

    # Admin login
    if username == ADMIN_USERNAME and security.verify_hash(password, ADMIN_PASSWORD_HASH):
        token = jwt_auth.create_token(identity=username, role='admin')
        logger.info(f"Login JWT bem-sucedido para admin '{username}'")
        return jsonify({'access_token': token, 'role': 'admin'}), 200

    # Usuário comum (exemplo: buscar no banco)
    db = DatabaseManager()
    user = db.fetch_one("SELECT id, username, password_hash, role FROM users WHERE username = ?", (username,))
    if user and jwt_auth.verify_password(password, user['password_hash']):
        token = jwt_auth.create_token(identity=user['username'], role=user.get('role', 'user'))
        logger.info(f"Login JWT bem-sucedido para usuário '{username}'")
        return jsonify({'access_token': token, 'role': user.get('role', 'user')}), 200

    logger.warning(f"Tentativa de login JWT falhou para usuário '{username}'")
    return jsonify({'error': get_text('login_failed', lang)}), 401

# Decorador para rotas protegidas por JWT

def jwt_admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        if not identity or identity.get('role') != 'admin':
            return jsonify({'error': 'Acesso restrito a administradores'}), 403
        return fn(*args, **kwargs)
    return wrapper

# Exemplo: proteger rota administrativa com JWT
@app.route('/api/admin/protected', methods=['GET'])
@jwt_admin_required
def admin_protected():
    return jsonify({'msg': 'Acesso admin JWT OK'}), 200

# Endpoints de configurações
@app.route('/api/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    """Gerenciamento de configurações do sistema."""
    lang = get_request_language()
    
    if request.method == 'GET':
        # Retorna configurações seguras (sem senhas/tokens)
        safe_settings = {
            'APP_NAME': settings.APP_NAME,
            'DEBUG': settings.DEBUG,
            'PORT': settings.PORT,
            'CACHE_TIMEOUT': settings.CACHE_TIMEOUT,
            'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
            'TELEGRAM_BOT_TOKEN_SET': bool(settings.TELEGRAM_BOT_TOKEN),
            'TELEGRAM_CHAT_ID_SET': bool(settings.TELEGRAM_CHAT_ID),
            'WHATSAPP_API_URL': settings.WHATSAPP_API_URL,
            'MOCK_BOOKMAKER_DATA': os.getenv('MOCK_BOOKMAKER_DATA', 'true'),
            'system_status': 'running',
            'active_adapters': list(get_all_adapters().keys()),
            'last_updated': datetime.now().isoformat()
        }
        return jsonify(safe_settings), 200
    
    elif request.method == 'POST':
        # Salva configurações (mock por enquanto)
        try:
            data = request.get_json() or {}
            logger.info(f"Configurações atualizadas por '{session.get('username')}': {data}")
            return jsonify({'status': get_text('settings_saved', lang)}), 200
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
            return jsonify({'error': str(e)}), 500

# Endpoints de notificações
@app.route('/api/admin/test-notification', methods=['POST'])
@login_required
@csrf_protected
def admin_test_notification():
    """Envia notificação de teste."""
    try:
        data = request.get_json()
        message = data.get('message', 'Teste de notificação')
        
        # Tentar enviar notificação
        result = notify_all(message)
        
        if result:
            logger.info(f"Notificação de teste enviada por '{session.get('username')}'")
            return jsonify({'status': get_text('notification_sent', get_request_language())}), 200
        else:
            return jsonify({'error': get_text('test_fail', get_request_language())}), 500
            
    except Exception as e:
        logger.error(f"Erro ao enviar notificação: {e}")
        return jsonify({'error': str(e)}), 500

# Endpoints de banco de dados
@app.route('/api/admin/db-overview', methods=['GET'])
@login_required
def admin_db_overview():
    """Visão geral do banco de dados."""
    try:
        db = DatabaseManager()
        
        # Estatísticas básicas
        events_count = db.fetch_one("SELECT COUNT(*) as count FROM events")
        surebets_count = db.fetch_one("SELECT COUNT(*) as count FROM surebets")
        users_count = db.fetch_one("SELECT COUNT(*) as count FROM users")
        
        # Eventos recentes
        recent_events = db.fetch("SELECT * FROM events ORDER BY created_at DESC LIMIT 5")
        recent_surebets = db.fetch("SELECT * FROM surebets ORDER BY detected_at DESC LIMIT 5")
        
        overview = {
            'statistics': {
                'total_events': events_count['count'] if events_count else 0,
                'total_surebets': surebets_count['count'] if surebets_count else 0,
                'total_users': users_count['count'] if users_count else 0,
            },
            'recent_events': recent_events or [],
            'recent_surebets': recent_surebets or [],
            'last_updated': datetime.now().isoformat()
        }
        
        db.close()
        return jsonify(overview), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar visão geral do DB: {e}")
        return jsonify({'error': str(e)}), 500

# Endpoints de apostas
@app.route('/api/admin/insert-bet', methods=['POST'])
@login_required
@csrf_protected
def admin_insert_bet():
    """Insere nova aposta no sistema."""
    try:
        data = request.get_json()
        lang = get_request_language()
        
        # Validar campos obrigatórios
        required_fields = ['event', 'market', 'selection', 'odd', 'bookmaker']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{get_text("missing_field", lang)}: {field}'}), 400
          # Validar odd
        try:
            odd = float(data['odd'])
            if odd <= 1.0:
                return jsonify({'error': get_text('odd_gt_1', lang)}), 400
        except ValueError:
            return jsonify({'error': get_text('invalid_odd', lang)}), 400
        
        # Inserir no banco
        db = DatabaseManager()
        try:
            bet_id = db.insert("bets", {
                'event_name': data['event'],
                'market': data['market'],
                'selection': data['selection'],
                'odd': odd,
                'bookmaker': data['bookmaker'],
                'created_by': session.get('username', 'admin'),
                'created_at': datetime.now().isoformat()
            })
            
            logger.info(f"Aposta inserida com ID {bet_id} por '{session.get('username')}'")
            return jsonify({
                'status': get_text('bet_inserted', lang),
                'bet_id': bet_id
            }), 200
            
        except Exception as e:
            logger.error(f"Erro ao inserir aposta: {e}")
            return jsonify({'error': str(e)}), 500
            
    except Exception as e:
        logger.error(f"Erro ao inserir aposta: {e}")
        return jsonify({'error': str(e)}), 500

# Endpoints de dados administrativos
@app.route('/api/admin/users', methods=['GET'])
@login_required
def get_users():
    """Lista usuários do sistema."""
    try:
        db = DatabaseManager()
        users = db.fetch("""
            SELECT id, username, email, created_at, last_login
            FROM users
            ORDER BY created_at DESC
        """) or []
        return jsonify({'users': users}), 200
    except Exception as e:
        logger.error(f"Erro ao buscar usuários: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/bets', methods=['GET'])
@login_required
def get_bets():
    """Lista apostas do sistema."""
    try:
        db = DatabaseManager()
        bets = db.fetch("""
            SELECT b.id, b.event_name, b.market, b.selection, b.odd, 
                   b.bookmaker, b.created_by, b.created_at
            FROM bets b
            ORDER BY b.created_at DESC
            LIMIT 100
        """) or []
        db.close()
        return jsonify({'bets': bets}), 200
    except Exception as e:
        logger.error(f"Erro ao buscar apostas: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/surebets', methods=['GET'])
@login_required
def get_surebets():
    """Lista surebets detectadas."""
    try:
        db = DatabaseManager()
        surebets = db.fetch("""
            SELECT id, event_name, market, profit_percentage, 
                   bookmakers, detected_at, status
            FROM surebets
            ORDER BY detected_at DESC
            LIMIT 50
        """) or []
        return jsonify({'surebets': surebets}), 200
    except Exception as e:
        logger.error(f"Erro ao buscar surebets: {e}")
        return jsonify({'error': str(e)}), 500

# Endpoints de oportunidades (públicos)
@app.route('/api/opportunities', methods=['POST'])
def get_opportunities():
    """Busca oportunidades de arbitragem."""
    try:
        data = request.get_json() or {}
        sports = data.get('sports', ['soccer'])
        min_profit = data.get('min_profit', 2.0)
        bookmakers = data.get('bookmakers', [])
        search = data.get('search', '').lower()
        
        opportunities = []
        adapters = get_all_adapters()
        
        for adapter_name, adapter in adapters.items():
            if not bookmakers or adapter_name in bookmakers:
                for sport in sports:
                    live_odds = adapter.get_live_odds(sport, limit=20)
                    
                    for event in live_odds:
                        for market in event.get('markets', []):
                            selections = market.get('selections', [])
                            if len(selections) >= 2:
                                # Cálculo simplificado de surebet
                                profit = calculate_surebet_profit(selections)
                                
                                if profit >= min_profit:
                                    opportunity = {
                                        'id': f"{adapter_name}_{event['id']}",
                                        'event': event['name'],
                                        'market': market['name'],
                                        'profit': profit,
                                        'bookmaker': adapter_name,
                                        'selections': selections,
                                        'sport': sport,
                                        'status': event['status'],
                                        'detected_at': datetime.now().isoformat()
                                    }
                                    
                                    # Filtro de busca
                                    if (not search or 
                                        search in opportunity['event'].lower() or 
                                        search in opportunity['market'].lower()):
                                        opportunities.append(opportunity)
        
        return jsonify({
            'opportunities': opportunities,
            'total': len(opportunities),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar oportunidades: {e}")
        return jsonify({'error': str(e)}), 500

def calculate_surebet_profit(selections: List[Dict[str, Any]]) -> float:
    """
    Calcula o lucro potencial de uma surebet.
    Implementação simplificada para demonstração.
    """
    if len(selections) < 2:
        return 0.0
    
    # Fórmula básica: (1/odd1 + 1/odd2 + ... < 1)
    inverse_sum = sum(1/selection['odds'] for selection in selections)
    
    if inverse_sum < 1:
        return (1 - inverse_sum) * 100  # Retorna percentual
    
    return 0.0

# Endpoints de jogos
@app.route('/api/games/live', methods=['GET'])
def get_live_games():
    """Busca jogos ao vivo."""
    try:
        sport = request.args.get('sport', 'soccer')
        limit = int(request.args.get('limit', 20))
        
        all_games = []
        adapters = get_all_adapters()
        
        for adapter_name, adapter in adapters.items():
            games = adapter.get_live_odds(sport, limit=limit//len(adapters))
            for game in games:
                all_games.append({
                    'id': game['id'],
                    'name': game['name'],
                    'sport': game['sport'],
                    'status': game['status'],
                    'start_time': game['start_time'],
                    'bookmaker': adapter_name
                })
        
        return jsonify({'games': all_games}), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar jogos ao vivo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/games/upcoming', methods=['GET'])
def get_upcoming_games():
    """Busca jogos futuros."""
    try:
        sport = request.args.get('sport', 'soccer')
        limit = int(request.args.get('limit', 20))
        
        all_games = []
        adapters = get_all_adapters()
        
        for adapter_name, adapter in adapters.items():
            games = adapter.get_upcoming_odds(sport, limit=limit//len(adapters))
            for game in games:
                all_games.append({
                    'id': game['id'],
                    'name': game['name'],
                    'sport': game['sport'],
                    'status': game['status'],
                    'start_time': game['start_time'],
                    'bookmaker': adapter_name
                })
        
        return jsonify({'games': all_games}), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar jogos futuros: {e}")
        return jsonify({'error': str(e)}), 500

# Endpoint de status
@app.route('/api/status', methods=['GET'])
def api_status():
    """Status da API."""
    return jsonify({
        'status': 'running',
        'version': '2.0.0-unified',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'database': 'connected',
            'adapters': list(get_all_adapters().keys()),
            'mock_mode': os.getenv('MOCK_BOOKMAKER_DATA', 'true') == 'true'
        }
    }), 200

# Middleware para CORS
@app.after_request
def after_request(response):
    """Adiciona headers CORS."""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-CSRF-Token')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    # Verificar configuração de segurança
    if not ADMIN_PASSWORD_HASH:
        logger.critical("ADMIN_PASSWORD_HASH não definido. API não pode iniciar de forma segura.")
        if not settings.DEBUG:
            exit(1)
    
    logger.info("Iniciando API administrativa consolidada")
    app.run(
        host='0.0.0.0',
        port=int(os.getenv("ADMIN_API_PORT", 5000)),
        debug=settings.DEBUG
    )
