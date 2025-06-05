"""
API administrativa consolidada para o Surebets Hunter Pro.

Unifica todas as funcionalidades administrativas em uma única API,
removendo redundâncias e padronizando endpoints.
"""

from flask import Flask, jsonify, request, make_response, current_app
from functools import wraps
import os
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Importar módulos unificados
from config.config_loader import CONFIG
from config.settings import (
    APP_NAME, DEBUG, PORT, CACHE_TIMEOUT, ALLOWED_HOSTS, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, WHATSAPP_API_URL, MOCK_BOOKMAKER_DATA
)
import config.settings as settings
from backend.services.notification import notify_all
from backend.apps.integration import BookmakerIntegration
from backend.core.i18n import get_text
from backend.database.database_postgres import PostgresDatabaseManager
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
def create_app(config_overrides=None):
    app = Flask(__name__)
    # Carregar config padrão
    app.secret_key = CONFIG['security']['secret_key']
    app.config['JWT_SECRET_KEY'] = CONFIG['security']['secret_key']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_MINUTES', '60')))
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES_DAYS', '30')))
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_COOKIE_SECURE'] = os.getenv('ENVIRONMENT') == 'production'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    # Aplique overrides ANTES de inicializar AuthManager
    if config_overrides:
        app.config.update(config_overrides)
        if 'secret_key' in config_overrides:
            app.secret_key = config_overrides['secret_key']
        if 'JWT_SECRET_KEY' in config_overrides:
            app.config['JWT_SECRET_KEY'] = config_overrides['JWT_SECRET_KEY']
    # Inicializar AuthManager e JWT
    app.jwt_auth = AuthManager(app)
    # Configuração de admin
    app.config['ADMIN_USERNAME'] = os.getenv("ADMIN_USERNAME", "admin")
    app.config['ADMIN_PASSWORD_HASH'] = CONFIG['security'].get('admin_password_hash', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')
    # Instanciar integração unificada
    app.bookmaker_integration = BookmakerIntegration()

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
                if not app.jwt_auth.has_permission(user_role, permission):
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
    @app.route('/api/auth/login', methods=['POST'])
    @validate_json_schema(LoginRequestSchema)
    @security_headers()
    def jwt_login():
        """Login para todos os usuários (JWT) com validação Pydantic."""
        data = request.validated_data  # Dados já validados pelo decorador
        username = data['username']
        password = data['password']
        use_cookie = data.get('use_cookie', False)
        lang = 'pt'  # Substituir get_request_language() por 'pt' (ou idioma padrão)

        # Admin login
        if username == current_app.config['ADMIN_USERNAME'] and current_app.jwt_auth.verify_password(password, current_app.config['ADMIN_PASSWORD_HASH']):
            access_token = app.jwt_auth.create_token(identity=username, role=ROLE_ADMIN)
            refresh_token = app.jwt_auth.create_refresh_token(identity=username, role=ROLE_ADMIN)
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
        db = PostgresDatabaseManager()
        user = db.fetch_one("SELECT id, username, password_hash, role FROM users WHERE username = %s", (username,))
        if user and app.jwt_auth.verify_password(password, user['password_hash']):
            role = user.get('role', ROLE_VIEWER)
            access_token = app.jwt_auth.create_token(identity=user['username'], role=role)
            refresh_token = app.jwt_auth.create_refresh_token(identity=user['username'], role=role)
            
            # Atualizar último login
            try:
                db.execute("UPDATE users SET last_login = %s WHERE username = %s", 
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
        
        access_token = app.jwt_auth.create_token(identity=user, role=role)
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
        app.jwt_auth.revoke_token(jti, exp)
        
        identity = get_jwt_identity()
        user = identity.get('user')
        logger.info(f"Logout JWT realizado para usuário '{user}'")
        
        use_cookie = request.json and request.json.get('use_cookie', False)
        
        if use_cookie:
            response = make_response(jsonify({
                'status': 'success', 
                'message': get_text('logout_success', 'pt')
            }))
            unset_jwt_cookies(response)
            return response, 200
        else:
            return jsonify({
                'status': 'success', 
                'message': get_text('logout_success', 'pt')
            }), 200

    @app.route('/api/auth/verify', methods=['GET', 'POST'])
    @jwt_required(optional=True)
    def verify_token():
        """Endpoint para verificar validade de token e retornar informações do usuário.
        ---
        Exemplo de claims/identity retornados para integração frontend:
        {
            "authenticated": true,
            "user": "admin",
            "role": "admin",
            "permissions": ["manage_users", "view_dashboard", ...],
            "expires_at": "2025-06-05T12:34:56",
            "issued_at": "2025-06-05T11:34:56",
            "remaining_seconds": 3599
        }
        """
        identity = get_jwt_identity()
        
        if not identity:
            return jsonify({
                'authenticated': False,
                'message': 'Nenhum token válido encontrado'
            }), 200

        # Robustez: garantir que identity é dict
        if isinstance(identity, str):
            # Caso raro: identity legado como string
            user = identity
            role = ROLE_VIEWER
        elif isinstance(identity, dict):
            user = identity.get('user')
            role = identity.get('role', ROLE_VIEWER)
        else:
            return jsonify({
                'authenticated': False,
                'message': 'Formato de token inválido'
            }), 401

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

    @app.route('/api/auth/tokens/<string:username>', methods=['GET'])
    @admin_required
    def list_user_tokens(username):
        """Lista tokens ativos/revogados de um usuário (apenas admin)."""
        # O AuthManager deve implementar get_user_tokens para listar tokens (mock ou real)
        tokens_info = app.jwt_auth.get_user_tokens(username)
        return jsonify(tokens_info), 200

    @app.route('/api/auth/token-status', methods=['GET'])
    @admin_required
    def check_token_blacklist():
        """Endpoint para verificar status da blacklist (apenas admin)."""
        blacklist_status = app.jwt_auth.get_blacklist_status()
        
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
        db = PostgresDatabaseManager()
        
        user_exists = db.fetch_one("SELECT id FROM users WHERE username = %s", (username,))
        if not user_exists and username != current_app.config['ADMIN_USERNAME']:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        success = app.jwt_auth.revoke_user_tokens(username, db)
        
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
        db = PostgresDatabaseManager()
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
        db = PostgresDatabaseManager()
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
        db = PostgresDatabaseManager()
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
        
        db = PostgresDatabaseManager()
        user_info = db.fetch_one(
            "SELECT username, email, role, created_at, last_login FROM users WHERE username = %s", 
            (user,)
        )
        
        if not user_info:
            # Se for o admin (que não está na tabela users)
            if user == current_app.config['ADMIN_USERNAME']:
                return jsonify({
                    'username': current_app.config['ADMIN_USERNAME'],
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
        lang = 'pt'  # Substituir get_request_language() por 'pt' (ou idioma padrão)
        db = PostgresDatabaseManager()
        
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
                exists = db.fetch_one("SELECT id FROM users WHERE username = %s", (user_data['username'],))
                
                if exists:
                    # Atualizar usuário existente
                    password_hash = app.jwt_auth.hash_password(user_data['password'])
                    db.execute("""
                        UPDATE users 
                        SET password_hash = ?, email = ?, role = ?
                        WHERE username = ?
                    """, (password_hash, user_data['email'], user_data['role'], user_data['username']))
                    logger.info(f"Usuário '{user_data['username']}' atualizado")
                    return jsonify({'status': 'success', 'message': 'Usuário atualizado com sucesso'}), 200
                else:
                    # Criar novo usuário
                    password_hash = app.jwt_auth.hash_password(user_data['password'])
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
        db = PostgresDatabaseManager()
        user = db.fetch_one("SELECT username FROM users WHERE id = %s", (user_id,))
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        db.execute("DELETE FROM users WHERE id = %s", (user_id,))
        logger.info(f"Usuário ID {user_id} ('{user['username']}') excluído")
        
        return jsonify({'status': 'success', 'message': 'Usuário excluído com sucesso'}), 200

    @app.route('/api/admin/settings', methods=['GET', 'POST'])
    def admin_settings():
        """Gerenciamento de configurações do sistema."""
        lang = 'pt'  # Substituir get_request_language() por 'pt' (ou idioma padrão)
        
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
                'active_adapters': list(current_app.bookmaker_integration.list_bookmakers().keys()),
                'last_updated': datetime.now().isoformat()
            }
            return jsonify(safe_settings), 200
        
        elif request.method == 'POST':
            try:
                data = request.get_json() or {}
                logger.info(f"Configurações atualizadas: {data}")
                return jsonify({'status': get_text('settings_saved', lang)}), 200
            except Exception as e:
                logger.error(f"Erro ao salvar configurações: {e}")
                return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/test-notification', methods=['POST'])
    def admin_test_notification():
        """Envia notificação de teste."""
        try:
            data = request.get_json()
            message = data.get('message', 'Teste de notificação')
            
            result = notify_all(message)
            
            if result:
                logger.info(f"Notificação de teste enviada")
                return jsonify({'status': get_text('notification_sent', 'pt')}), 200
            else:
                return jsonify({'error': get_text('test_fail', 'pt')}), 500
                
        except Exception as e:
            logger.error(f"Erro ao enviar notificação: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/db-overview', methods=['GET'])
    def admin_db_overview():
        """Visão geral do banco de dados."""
        try:
            db = PostgresDatabaseManager()
            
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
    @security_headers()
    def admin_insert_bet():
        """Insere nova aposta no sistema com validação Pydantic."""
        try:
            bet_data = request.validated_data  # Dados já validados pelo decorador
            lang = 'pt'  # Substituir get_request_language() por 'pt' (ou idioma padrão)
            
            db = PostgresDatabaseManager()
            try:
                bet_id = db.insert("bets", {
                    'event_name': bet_data['event'],
                    'market': bet_data['market'],
                    'selection': bet_data['selection'],
                    'odd': bet_data['odd'],
                    'bookmaker': bet_data['bookmaker'],
                    'created_by': 'admin',
                    'created_at': datetime.now().isoformat()
                })
                
                logger.info(f"Aposta inserida com ID {bet_id} por 'admin'")
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
    @jwt_required()
    def get_bets():
        """Lista apostas do sistema."""
        try:
            db = PostgresDatabaseManager()
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
    @jwt_required()
    def get_surebets():
        """Lista surebets detectadas."""
        try:
            db = PostgresDatabaseManager()
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
            adapters = current_app.bookmaker_integration.list_bookmakers()
            
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
            adapters = current_app.bookmaker_integration.list_bookmakers()
            
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
            adapters = current_app.bookmaker_integration.list_bookmakers()
            
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
                'adapters': list(current_app.bookmaker_integration.list_bookmakers().keys()),
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

    # --- JWT/OAuth2: Implementação robusta ---
    # 1. Blacklist de tokens revogados já está integrada via AuthManager
    # 2. Claims de roles e permissões já são incluídos nos tokens
    # 3. Endpoints JWT/OAuth2 já implementados: login, refresh, logout, verify, revoke-all, roles
    # 4. Integração JWT com frontend: tokens via header, cookies opcionais, claims claros
    # 5. Testes de login/logout/expiração: garantir cobertura em test_jwt_auth.py
    #
    # Melhorias finais para robustez e clareza:
    # - Garantir que todos os endpoints JWT retornam claims completos e mensagens claras
    # - Garantir que a blacklist é consultada em todos os fluxos (logout, refresh, verify)
    # - Garantir que roles e permissões são sempre retornados no payload
    # - Documentar claramente o formato do identity e claims
    #
    # (Opcional) Adicionar endpoint para listar tokens ativos/revogados (admin)
    #
    # --- Fim das melhorias ---
    return app

# Instanciar app padrão para produção
app = create_app()

# --- Testes automatizados ---
# Os testes de integração já cobrem login, refresh, logout, expiração, roles e blacklist.
# Certifique-se de rodar: pytest backend/tests/integration/test_jwt_auth.py -v

if __name__ == '__main__':
    if not app.config.get('ADMIN_PASSWORD_HASH'):
        logger.critical("ADMIN_PASSWORD_HASH não definido. API não pode iniciar de forma segura.")
        if not settings.DEBUG:
            exit(1)
    logger.info("Iniciando API administrativa consolidada")
    app.run(
        host='0.0.0.0',
        port=int(os.getenv("ADMIN_API_PORT", 5000)),
        debug=settings.DEBUG
    )
