from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta, datetime
import redis
import os
import logging
from config.config_loader import CONFIG

# Configuração de logging
logger = logging.getLogger(__name__)

# Roles do sistema
ROLE_ADMIN = 'admin'      # Acesso total ao sistema
ROLE_OPERATOR = 'operator'  # Pode operar apostas, gerenciar alertas
ROLE_VIEWER = 'viewer'    # Visualização apenas

# Mapeamento de permissões por role - sistema avançado de roles
ROLE_PERMISSIONS = {
    ROLE_ADMIN: {
        'can_manage_users': True,
        'can_delete_data': True,
        'can_configure_system': True,
        'can_manage_odds': True,
        'can_place_bets': True,
        'can_view_reports': True,
        'can_view_dashboard': True
    },
    ROLE_OPERATOR: {
        'can_manage_users': False,
        'can_delete_data': False,
        'can_configure_system': False,
        'can_manage_odds': True,
        'can_place_bets': True,
        'can_view_reports': True,
        'can_view_dashboard': True
    },
    ROLE_VIEWER: {
        'can_manage_users': False,
        'can_delete_data': False,
        'can_configure_system': False,
        'can_manage_odds': False,
        'can_place_bets': False,
        'can_view_reports': True,
        'can_view_dashboard': True
    }
}

# Exemplo de uso de configuração:
REDIS_URL = CONFIG.get('redis', {}).get('url', 'redis://localhost:6379/0')

class TokenBlacklist:
    def __init__(self, redis_url=None):
        self.redis = None
        if redis_url is None:
            redis_url = REDIS_URL
        if redis_url:
            try:
                self.redis = redis.from_url(redis_url)
                logger.info(f"Conectado ao Redis na URL: {redis_url}")
                # Testar conexão
                self.redis.ping()
            except redis.exceptions.ConnectionError as e:
                logger.warning(f"Falha na conexão com Redis: {e}. Usando blacklist em memória.")
                self.redis = None
        
        if not self.redis:
            # Fallback para uma implementação em memória para desenvolvimento
            logger.warning("Usando implementação em memória para blacklist de tokens")
            self._blacklist = {}
    
    def add_to_blacklist(self, jti, exp_timestamp):
        """Adiciona um token à blacklist"""
        try:
            if self.redis:
                # Calcular TTL (tempo até expiração)
                ttl = max(0, int(exp_timestamp - datetime.timestamp(datetime.now())))
                self.redis.set(f"token_blacklist:{jti}", "1", ex=ttl)
                logger.debug(f"Token {jti} adicionado à blacklist no Redis (expira em {ttl}s)")
            else:
                self._blacklist[jti] = exp_timestamp
                # Limpa tokens expirados da blacklist em memória
                now = datetime.timestamp(datetime.now())
                self._blacklist = {j: exp for j, exp in self._blacklist.items() if exp > now}
                logger.debug(f"Token {jti} adicionado à blacklist em memória")
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar token à blacklist: {e}")
            return False
    
    def is_blacklisted(self, jti):
        """Verifica se um token está na blacklist"""
        try:
            if self.redis:
                result = bool(self.redis.exists(f"token_blacklist:{jti}"))
                logger.debug(f"Token {jti} verificado no Redis: {'bloqueado' if result else 'válido'}")
                return result
            
            # Limpar tokens expirados da blacklist em memória
            now = datetime.timestamp(datetime.now())
            self._blacklist = {j: exp for j, exp in self._blacklist.items() if exp > now}
            result = jti in self._blacklist
            logger.debug(f"Token {jti} verificado em memória: {'bloqueado' if result else 'válido'}")
            return result
        except Exception as e:
            logger.error(f"Erro ao verificar token na blacklist: {e}")
            return False
            
    def clear_expired(self):
        """Limpa tokens expirados da blacklist (apenas para implementação em memória)"""
        if not self.redis:
            now = datetime.timestamp(datetime.now())
            old_count = len(self._blacklist)
            self._blacklist = {j: exp for j, exp in self._blacklist.items() if exp > now}
            new_count = len(self._blacklist)
            logger.info(f"Limpeza de blacklist: {old_count - new_count} tokens expirados removidos")
            return old_count - new_count
        return 0
        
    def get_blacklist_size(self):
        """Retorna o tamanho atual da blacklist"""
        if self.redis:
            try:
                size = self.redis.keys("token_blacklist:*")
                return len(size)
            except:
                return "N/A (Redis)"
        return len(self._blacklist)


class AuthManager:
    def __init__(self, app=None):
        self.jwt = None
        self.blacklist = TokenBlacklist(os.getenv('REDIS_URL'))
        self.refresh_tokens = {}  # Para controle avançado de refresh tokens
        if app:
            self.init_app(app)

    def init_app(self, app):
        # NÃO sobrescrever app.config['JWT_SECRET_KEY'] aqui!
        # Apenas garantir que os outros parâmetros estejam presentes
        if 'JWT_ACCESS_TOKEN_EXPIRES' not in app.config:
            app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_MINUTES', '60')))
        if 'JWT_REFRESH_TOKEN_EXPIRES' not in app.config:
            app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES_DAYS', '30')))
        # Configurar integração com frontend
        app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
        app.config['JWT_COOKIE_SECURE'] = os.getenv('ENVIRONMENT') == 'production'
        app.config['JWT_COOKIE_CSRF_PROTECT'] = True
        self.jwt = JWTManager(app)
        
        # Configurar callback para checar tokens na blacklist
        @self.jwt.token_in_blocklist_loader
        def check_if_token_revoked(jwt_header, jwt_payload):
            jti = jwt_payload["jti"]
            return self.blacklist.is_blacklisted(jti)
            
        # Adicionar informações ao payload do token JWT
        @self.jwt.additional_claims_loader
        def add_claims_to_jwt(identity):
            role = identity.get('role', ROLE_VIEWER)
            permissions = ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS[ROLE_VIEWER])
            return {
                'permissions': permissions,
                'created_at': datetime.now().timestamp()
            }
            
        # Callback para quando o token está expirado
        @self.jwt.expired_token_loader
        def expired_token_callback(jwt_header, jwt_payload):
            return {
                'status': 'error',
                'message': 'O token está expirado',
                'code': 'token_expired'
            }, 401
            
        # Callback para quando o token é inválido
        @self.jwt.invalid_token_loader
        def invalid_token_callback(error_string):
            return {
                'status': 'error',
                'message': 'Assinatura de token inválida',
                'code': 'invalid_token'
            }, 401

    def revoke_token(self, token_jti, exp_timestamp):
        """Revoga um token adicionando-o à blacklist"""
        return self.blacklist.add_to_blacklist(token_jti, exp_timestamp)

    def revoke_user_tokens(self, user_identity, db_connection=None):
        """Revoga todos os tokens de um usuário"""
        if db_connection:
            try:
                # Se tivermos uma conexão com o banco, registrar os tokens revogados
                db_connection.execute(
                    "INSERT INTO revoked_tokens (user_id, revoked_at) VALUES (?, ?)",
                    (user_identity, datetime.now().isoformat())
                )
                logger.info(f"Registrado revogação de todos os tokens para o usuário {user_identity}")
                return True
            except Exception as e:
                logger.error(f"Erro ao registrar revogação de tokens: {e}")
        
        return False

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)

    @staticmethod
    def verify_password(password, password_hash):
        return check_password_hash(password_hash, password)

    @staticmethod
    def create_token(identity, role):
        """Cria um access token com informações do usuário"""
        return create_access_token(identity={"user": identity, "role": role})

    @staticmethod
    def create_refresh_token(identity, role):
        """Cria um refresh token com informações do usuário"""
        return create_refresh_token(identity={"user": identity, "role": role})
        
    @staticmethod
    def is_role_authorized(required_roles, user_role):
        """Verifica se o usuário tem um dos papéis necessários"""
        if isinstance(required_roles, str):
            required_roles = [required_roles]
        return user_role in required_roles
        
    @staticmethod
    def has_permission(role, permission):
        """Verifica se o papel tem uma permissão específica"""
        role_perms = ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS[ROLE_VIEWER])
        return role_perms.get(permission, False)
        
    def get_blacklist_status(self):
        """Retorna status da blacklist para monitoramento"""
        return {
            'size': self.blacklist.get_blacklist_size(),
            'using_redis': self.blacklist.redis is not None,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_user_tokens(self, username):
        """Retorna lista de tokens ativos/revogados para um usuário (mock para demo/testes)."""
        # Em produção, isso deveria consultar um storage real de tokens emitidos/blacklistados        # Mock: retorna apenas tokens da blacklist em memória (apenas para desenvolvimento)
        active = []
        revoked = []
        if hasattr(self.blacklist, '_blacklist'):
            now = datetime.timestamp(datetime.now())
            for jti, exp in self.blacklist._blacklist.items():
                # Aqui não temos username real, pois a blacklist só armazena jti e exp
                # Em produção, seria necessário um storage real com relação jti <-> usuário
                if exp > now:
                    revoked.append(jti)
        return {
            'username': username,
            'active_tokens': active,
            'revoked_tokens': revoked,
            'active_count': len(active),
            'revoked_count': len(revoked)
        }
