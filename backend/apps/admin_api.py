"""
API administrativa consolidada para o Surebets Hunter Pro.

Unifica todas as funcionalidades administrativas em uma única API,
removendo redundâncias e padronizando endpoints.
"""

from flask import Flask, jsonify, request, session, make_response
from functools import wraps
import os
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Importar módulos unificados
from config import settings, security
from backend.services.notification import notify_all
from backend.apps.adapters import get_all_adapters
from backend.core.i18n import get_text
from database.database import DatabaseManager
from backend.core.auth import AuthManager, ROLE_ADMIN, ROLE_OPERATOR, ROLE_VIEWER, ROLE_PERMISSIONS
from backend.core.validation import (
    LoginRequestSchema, UserCreateSchema, BetInsertSchema, SearchParamsSchema,
    validate_json_schema, validate_args_schema, security_headers,
    sanitize_text, detect_sql_injection, detect_xss, log_security_event,
    SecurityError, ValidationError as CustomValidationError
)
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, get_jwt,
    verify_jwt_in_request, set_access_cookies, set_refresh_cookies,
    unset_jwt_cookies
)

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,  # Mude para DEBUG para capturar logs detalhados
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('surebets_app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
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

# Decoradores para autenticação baseada em sessão (legacy)
def login_required(f):
    """Decorador para proteger rotas que exigem login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return jsonify({'error': get_text('unauthorized')}), 401
        return f(*args, **kwargs)
    return decorated_function

def csrf_protected(f):
    """Decorador para proteção CSRF."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            token = request.headers.get('X-CSRF-Token') or (request.json.get('csrf_token') if request.json else None)
            if not token or token != session.get('csrf_token'):
                log_security_event('CSRF_VIOLATION', f'Missing or invalid CSRF token for {request.endpoint}')
                return jsonify({'error': 'CSRF token inválido'}), 403
        return f(*args, **kwargs)
    return decorated_function

def get_request_language() -> str:
    """Obtém o idioma da requisição."""
    return request.headers.get('Accept-Language', 'pt')[:2] or 'pt'

# Decoradores para autenticação JWT com base em roles
def role_required(allowed_roles):
    """Decorador para proteger rotas com base em roles JWT."""
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            if not identity:
                return jsonify({'error': 'Acesso não autorizado'}), 401
                
            user_role = identity.get('role', ROLE_VIEWER)
            if user_role not in allowed_roles:
                return jsonify({'error': 'Permissão insuficiente para acessar este recurso'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# Decorator baseado em permissões em vez de roles
def permission_required(permission):
    """Decorador para proteger rotas com base em permissões específicas."""
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            if not identity:
                return jsonify({'error': 'Acesso não autorizado'}), 401
                
            user_role = identity.get('role', ROLE_VIEWER)
            
            # Verificar se o role tem a permissão necessária
            if not jwt_auth.has_permission(user_role, permission):
                return jsonify({
                    'error': 'Permissão insuficiente', 
                    'required': permission
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# Atalhos para os roles mais comuns
def admin_required(fn):
    """Apenas administradores podem acessar."""
    return role_required([ROLE_ADMIN])(fn)

def operator_required(fn):
    """Administradores e operadores podem acessar."""
    return role_required([ROLE_ADMIN, ROLE_OPERATOR])(fn)

def viewer_required(fn):
    """Qualquer usuário autenticado pode acessar."""
    return role_required([ROLE_ADMIN, ROLE_OPERATOR, ROLE_VIEWER])(fn)

# Endpoints de autenticação com validação rigorosa
@app.route('/api/admin/login', methods=['POST'])
@security_headers()
def admin_login():
    """Endpoint de login administrativo com validação rigorosa."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON payload obrigatório'}), 400
        
        # Sanitizar entrada básica
        username = sanitize_text(data.get('username', ''))
        password = data.get('password', '')
        lang = get_request_language()
        
        if not username or not password:
            return jsonify({'error': get_text('missing_field', lang)}), 400
        
        # Verificar tentativas de ataques
        if detect_sql_injection(username) or detect_xss(username):
            log_security_event('ATTACK_ATTEMPT', f'SQL/XSS attempt in admin login: {username}')
            return jsonify({'error': 'Conteúdo suspeito detectado'}), 400
        
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
            log_security_event('LOGIN_FAILED', f'Failed admin login attempt: {username}')
            logger.warning(f"Tentativa de login falhou para usuário '{username}'")
            return jsonify({'error': get_text('login_failed', lang)}), 401
            
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        return jsonify({'error': get_text('error', get_request_language())}), 500

@app.route('/api/admin/logout', methods=['POST'])
@login_required
@security_headers()
def admin_logout():
    """Endpoint de logout administrativo."""
    username = session.get('username')
    session.clear()
    logger.info(f"Logout realizado para usuário '{username}'")
    return jsonify({'status': get_text('logout_success', get_request_language())}), 200

@app.route('/api/auth/login', methods=['POST'])
@validate_json_schema(LoginRequestSchema)
@security_headers()
def jwt_login():
    """Login para todos os usuários (JWT) com validação Pydantic."""
    data = request.validated_data  # Dados já validados pelo decorador
    username = data['username']
    password = data['password']
    use_cookie = data.get('use_cookie', False)
    lang = get_request_language()

    # Admin login
    if username == ADMIN_USERNAME and security.verify_hash(password, ADMIN_PASSWORD_HASH):
        access_token = jwt_auth.create_token(identity=username, role=ROLE_ADMIN)
        refresh_token = jwt_auth.create_refresh_token(identity=username, role=ROLE_ADMIN)
        logger.info(f"Login JWT bem-sucedido para admin '{username}'")
        
        if use_cookie:
            response = make_response(jsonify({
                'status': 'success',
                'role': ROLE_ADMIN,
                'permissions': ROLE_PERMISSIONS[ROLE_ADMIN]
            }))
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response, 200
        else:
            return jsonify({
                'access_token': access_token, 
                'refresh_token': refresh_token,
                'role': ROLE_ADMIN,
                'permissions': ROLE_PERMISSIONS[ROLE_ADMIN],
                'expires_in': int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_MINUTES', '60')) * 60
            }), 200

    # Usuário comum (buscar no banco)
    db = DatabaseManager()
    user = db.fetch_one("SELECT id, username, password_hash, role FROM users WHERE username = ?", (username,))
    if user and jwt_auth.verify_password(password, user['password_hash']):
        role = user.get('role', ROLE_VIEWER)
        access_token = jwt_auth.create_token(identity=user['username'], role=role)
        refresh_token = jwt_auth.create_refresh_token(identity=user['username'], role=role)
        
        # Atualizar último login
        try:
            db.execute("UPDATE users SET last_login = ? WHERE username = ?", 
                      (datetime.now().isoformat(), user['username']))
        except:
            logger.warning(f"Falha ao atualizar último login para usuário {username}")
            
        logger.info(f"Login JWT bem-sucedido para usuário '{username}' com role '{role}'")
        
        if use_cookie:
            response = make_response(jsonify({
                'status': 'success',
                'role': role,
                'permissions': ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS[ROLE_VIEWER])
            }))
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response, 200
        else:
            return jsonify({
                'access_token': access_token, 
                'refresh_token': refresh_token,
                'role': role,
                'permissions': ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS[ROLE_VIEWER]),
                'expires_in': int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_MINUTES', '60')) * 60
            }), 200

    log_security_event('LOGIN_FAILED', f'Failed JWT login attempt: {username}')
    logger.warning(f"Tentativa de login JWT falhou para usuário '{username}'")
    return jsonify({'error': get_text('login_failed', lang)}), 401

@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Endpoint para renovar access token usando refresh token."""
    identity = get_jwt_identity()
    user = identity.get('user')
    role = identity.get('role', ROLE_VIEWER)
    
    use_cookie = request.json and request.json.get('use_cookie', False)
    
    access_token = jwt_auth.create_token(identity=user, role=role)
    logger.info(f"Token renovado para usuário '{user}'")
    
    if use_cookie:
        response = make_response(jsonify({
            'status': 'success',
            'role': role,
            'permissions': ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS[ROLE_VIEWER])
        }))
        set_access_cookies(response, access_token)
        return response, 200
    else:
        return jsonify({
            'access_token': access_token,
            'role': role,
            'permissions': ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS[ROLE_VIEWER]),
            'expires_in': int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_MINUTES', '60')) * 60
        }), 200

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def jwt_logout():
    """Endpoint para logout JWT (adiciona token à blacklist)."""
    jti = get_jwt()["jti"]
    exp = get_jwt()["exp"]
    jwt_auth.revoke_token(jti, exp)
    
    identity = get_jwt_identity()
    user = identity.get('user')
    logger.info(f"Logout JWT realizado para usuário '{user}'")
    
    use_cookie = request.json and request.json.get('use_cookie', False)
    
    if use_cookie:
        response = make_response(jsonify({
            'status': 'success', 
            'message': get_text('logout_success', get_request_language())
        }))
        unset_jwt_cookies(response)
        return response, 200
    else:
        return jsonify({
            'status': 'success', 
            'message': get_text('logout_success', get_request_language())
        }), 200

@app.route('/api/auth/verify', methods=['GET', 'POST'])
@jwt_required(optional=True)
def verify_token():
    """Endpoint para verificar validade de token e retornar informações do usuário."""
    identity = get_jwt_identity()
    
    if not identity:
        return jsonify({
            'authenticated': False,
            'message': 'Nenhum token válido encontrado'
        }), 200
    
    # Token é válido, retornar informações do usuário
    user = identity.get('user')
    role = identity.get('role', ROLE_VIEWER)
    
    claims = get_jwt()
    expiry = datetime.fromtimestamp(claims['exp']).isoformat() if 'exp' in claims else None
    issued_at = datetime.fromtimestamp(claims['iat']).isoformat() if 'iat' in claims else None
    
    return jsonify({
        'authenticated': True,
        'user': user,
        'role': role,
        'permissions': ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS[ROLE_VIEWER]),
        'expires_at': expiry,
        'issued_at': issued_at,
        'remaining_seconds': claims.get('exp', 0) - datetime.now().timestamp() if 'exp' in claims else 0
    }), 200

@app.route('/api/auth/token-status', methods=['GET'])
@admin_required
def check_token_blacklist():
    """Endpoint para verificar status da blacklist (apenas admin)."""
    blacklist_status = jwt_auth.get_blacklist_status()
    
    tokens_stats = {
        'blacklist_size': blacklist_status['size'],
        'using_redis': blacklist_status['using_redis'],
        'timestamp': blacklist_status['timestamp']
    }
    
    return jsonify(tokens_stats), 200

@app.route('/api/auth/revoke-all/<string:username>', methods=['POST'])
@admin_required
def revoke_user_tokens(username):
    """Revoga todos os tokens para um usuário (apenas admin)."""
    db = DatabaseManager()
    
    user_exists = db.fetch_one("SELECT id FROM users WHERE username = ?", (username,))
    if not user_exists and username != ADMIN_USERNAME:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    success = jwt_auth.revoke_user_tokens(username, db)
    
    if success:
        return jsonify({
            'status': 'success',
            'message': f'Todos os tokens para {username} foram revogados'
        }), 200
    else:
        return jsonify({
            'status': 'warning',
            'message': f'Tokens para {username} foram marcados para revogação, mas tokens individuais ainda precisarão ser invalidados ao serem usados'
        }), 200

@app.route('/api/auth/roles', methods=['GET'])
@admin_required
def get_roles():
    """Retorna informações sobre os roles e suas permissões."""
    roles_info = {
        'available_roles': [ROLE_ADMIN, ROLE_OPERATOR, ROLE_VIEWER],
        'permissions_map': ROLE_PERMISSIONS,
        'definition': {
            ROLE_ADMIN: 'Acesso total ao sistema',
            ROLE_OPERATOR: 'Pode operar apostas e gerenciar alertas',
            ROLE_VIEWER: 'Visualização apenas'
        }
    }
    
    return jsonify(roles_info), 200

@app.route('/api/admin/protected', methods=['GET'])
@admin_required
def admin_protected():
    return jsonify({'msg': 'Acesso admin JWT OK'}), 200

@app.route('/api/admin/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    """Dashboard administrativo com dados sensíveis (somente admin)."""
    db = DatabaseManager()
    users_count = db.fetch_one("SELECT COUNT(*) as count FROM users")
    surebets_count = db.fetch_one("SELECT COUNT(*) as count FROM surebets")
    recent_surebets = db.fetch("SELECT * FROM surebets ORDER BY detected_at DESC LIMIT 10")
    
    identity = get_jwt_identity()
    return jsonify({
        'user': identity.get('user'),
        'role': identity.get('role'),
        'stats': {
            'users': users_count['count'] if users_count else 0,
            'surebets': surebets_count['count'] if surebets_count else 0,
        },
        'recent_surebets': recent_surebets or [],
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/operator/dashboard', methods=['GET'])
@operator_required
def operator_dashboard():
    """Dashboard para operadores (admins e operadores)."""
    db = DatabaseManager()
    surebets_count = db.fetch_one("SELECT COUNT(*) as count FROM surebets")
    active_surebets = db.fetch("SELECT * FROM surebets WHERE status = 'active' ORDER BY detected_at DESC LIMIT 15")
    
    identity = get_jwt_identity()
    return jsonify({
        'user': identity.get('user'),
        'role': identity.get('role'),
        'stats': {
            'surebets': surebets_count['count'] if surebets_count else 0,
            'active': len(active_surebets) if active_surebets else 0
        },
        'active_surebets': active_surebets or [],
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/user/dashboard', methods=['GET'])
@viewer_required
def user_dashboard():
    """Dashboard para usuários básicos (todos os roles têm acesso)."""
    db = DatabaseManager()
    total_opportunities = db.fetch_one("SELECT COUNT(*) as count FROM surebets")
    
    identity = get_jwt_identity()
    return jsonify({
        'user': identity.get('user'),
        'role': identity.get('role'),
        'stats': {
            'opportunities': total_opportunities['count'] if total_opportunities else 0,
        },
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/user/profile', methods=['GET'])
@jwt_required()
def user_profile():
    """Perfil do usuário autenticado."""
    identity = get_jwt_identity()
    user = identity.get('user')
    role = identity.get('role')
    
    db = DatabaseManager()
    user_info = db.fetch_one(
        "SELECT username, email, role, created_at, last_login FROM users WHERE username = ?", 
        (user,)
    )
    
    if not user_info:
        # Se for o admin (que não está na tabela users)
        if user == ADMIN_USERNAME:
            return jsonify({
                'username': ADMIN_USERNAME,
                'role': ROLE_ADMIN,
                'permissions': ROLE_PERMISSIONS[ROLE_ADMIN]
            }), 200
        else:
            return jsonify({'error': 'Perfil não encontrado'}), 404
    
    # Adicionar permissões baseadas no role
    user_info['permissions'] = ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS[ROLE_VIEWER])
    
    return jsonify(user_info), 200

@app.route('/api/admin/users', methods=['GET', 'POST'])
@admin_required
@security_headers()
def manage_users():
    """Gerenciar usuários (somente admin) com validação rigorosa."""
    lang = get_request_language()
    db = DatabaseManager()
    
    if request.method == 'GET':
        users = db.fetch("""
            SELECT id, username, email, role, created_at, last_login
            FROM users
            ORDER BY created_at DESC
        """) or []
        return jsonify({'users': users}), 200
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'JSON payload obrigatório'}), 400
            
            # Validar com Pydantic
            validated_user = UserCreateSchema(**data)
            user_data = validated_user.dict()
            
            # Verificar se usuário já existe
            exists = db.fetch_one("SELECT id FROM users WHERE username = ?", (user_data['username'],))
            
            if exists:
                # Atualizar usuário existente
                password_hash = jwt_auth.hash_password(user_data['password'])
                db.execute("""
                    UPDATE users 
                    SET password_hash = ?, email = ?, role = ?
                    WHERE username = ?
                """, (password_hash, user_data['email'], user_data['role'], user_data['username']))
                logger.info(f"Usuário '{user_data['username']}' atualizado")
                return jsonify({'status': 'success', 'message': 'Usuário atualizado com sucesso'}), 200
            else:
                # Criar novo usuário
                password_hash = jwt_auth.hash_password(user_data['password'])
                db.insert("users", {
                    'username': user_data['username'],
                    'password_hash': password_hash,
                    'email': user_data['email'],
                    'role': user_data['role'],
                    'created_at': datetime.now().isoformat(),
                    'last_login': None
                })
                logger.info(f"Novo usuário '{user_data['username']}' criado com role '{user_data['role']}'")
                return jsonify({'status': 'success', 'message': 'Usuário criado com sucesso'}), 201
                
        except CustomValidationError as e:
            log_security_event('VALIDATION_ERROR', f'User creation validation failed: {str(e)}')
            return jsonify({'error': 'Dados inválidos', 'details': str(e)}), 400
        except Exception as e:
            logger.error(f"Erro ao gerenciar usuário: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Excluir usuário (somente admin)."""
    db = DatabaseManager()
    user = db.fetch_one("SELECT username FROM users WHERE id = ?", (user_id,))
    
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    logger.info(f"Usuário ID {user_id} ('{user['username']}') excluído")
    
    return jsonify({'status': 'success', 'message': 'Usuário excluído com sucesso'}), 200

@app.route('/api/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    """Gerenciamento de configurações do sistema."""
    lang = get_request_language()
    
    if request.method == 'GET':
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
        try:
            data = request.get_json() or {}
            logger.info(f"Configurações atualizadas por '{session.get('username')}': {data}")
            return jsonify({'status': get_text('settings_saved', lang)}), 200
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/admin/test-notification', methods=['POST'])
@login_required
@csrf_protected
def admin_test_notification():
    """Envia notificação de teste."""
    try:
        data = request.get_json()
        message = data.get('message', 'Teste de notificação')
        
        result = notify_all(message)
        
        if result:
            logger.info(f"Notificação de teste enviada por '{session.get('username')}'")
            return jsonify({'status': get_text('notification_sent', get_request_language())}), 200
        else:
            return jsonify({'error': get_text('test_fail', get_request_language())}), 500
            
    except Exception as e:
        logger.error(f"Erro ao enviar notificação: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/db-overview', methods=['GET'])
@login_required
def admin_db_overview():
    """Visão geral do banco de dados."""
    try:
        db = DatabaseManager()
        
        events_count = db.fetch_one("SELECT COUNT(*) as count FROM events")
        surebets_count = db.fetch_one("SELECT COUNT(*) as count FROM surebets")
        users_count = db.fetch_one("SELECT COUNT(*) as count FROM users")
        
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

@app.route('/api/admin/insert-bet', methods=['POST'])
@validate_json_schema(BetInsertSchema)
@login_required
@csrf_protected
@security_headers()
def admin_insert_bet():
    """Insere nova aposta no sistema com validação Pydantic."""
    try:
        bet_data = request.validated_data  # Dados já validados pelo decorador
        lang = get_request_language()
        
        db = DatabaseManager()
        try:
            bet_id = db.insert("bets", {
                'event_name': bet_data['event'],
                'market': bet_data['market'],
                'selection': bet_data['selection'],
                'odd': bet_data['odd'],
                'bookmaker': bet_data['bookmaker'],
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

@app.route('/api/opportunities', methods=['POST'])
@validate_args_schema(SearchParamsSchema)
@security_headers()
def get_opportunities():
    """Busca oportunidades de arbitragem com validação de parâmetros."""
    try:
        # Dados de URL já validados
        search_params = getattr(request, 'validated_args', {})
        
        data = request.get_json() or {}
        sports = data.get('sports', ['soccer'])
        min_profit = float(data.get('min_profit', 2.0))
        bookmakers = data.get('bookmakers', [])
        search = search_params.get('query', '').lower()
        
        # Validar min_profit
        if min_profit < 0 or min_profit > 100:
            return jsonify({'error': 'min_profit deve estar entre 0 e 100'}), 400
        
        opportunities = []
        adapters = get_all_adapters()
        
        for adapter_name, adapter in adapters.items():
            if not bookmakers or adapter_name in bookmakers:
                for sport in sports:
                    try:
                        live_odds = adapter.get_live_odds(sport, limit=20)
                        
                        for event in live_odds:
                            for market in event.get('markets', []):
                                selections = market.get('selections', [])
                                if len(selections) >= 2:
                                    profit = calculate_surebet_profit(selections)
                                    
                                    if profit >= min_profit:
                                        opportunity = {
                                            'id': f"{adapter_name}_{event['id']}",
                                            'event': sanitize_text(event['name']),
                                            'market': sanitize_text(market['name']),
                                            'profit': round(profit, 2),
                                            'bookmaker': adapter_name,
                                            'selections': selections,
                                            'sport': sport,
                                            'status': event['status'],
                                            'detected_at': datetime.now().isoformat()
                                        }
                                        
                                        if (not search or 
                                            search in opportunity['event'].lower() or 
                                            search in opportunity['market'].lower()):
                                            opportunities.append(opportunity)
                    except Exception as adapter_error:
                        logger.warning(f"Erro no adapter {adapter_name}: {adapter_error}")
                        continue
        
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
    
    inverse_sum = sum(1/selection['odds'] for selection in selections)
    
    if inverse_sum < 1:
        return (1 - inverse_sum) * 100
    
    return 0.0

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

@app.after_request
def after_request(response):
    """Adiciona headers CORS."""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-CSRF-Token')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
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
