import pytest
import os
import sys
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Adicionar diretório pai ao path do Python para importar módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.core.auth import AuthManager, TokenBlacklist, ROLE_ADMIN, ROLE_OPERATOR, ROLE_VIEWER
from flask import Flask
from flask_jwt_extended import create_access_token, get_jwt_identity, decode_token

class TestTokenBlacklist:
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.blacklist = TokenBlacklist()  # Implementação em memória

    def test_add_token_to_blacklist(self):
        """Testa adicionar um token à blacklist."""
        # Arrange
        jti = "test_token_123"
        exp_time = int((datetime.now() + timedelta(hours=1)).timestamp())
        
        # Act
        self.blacklist.add_to_blacklist(jti, exp_time)
        
        # Assert
        assert jti in self.blacklist._blacklist
        assert self.blacklist.is_blacklisted(jti) == True

    def test_expired_token_cleanup(self):
        """Testa se tokens expirados são limpos da blacklist."""
        # Arrange
        expired_jti = "expired_token_456"
        valid_jti = "valid_token_789"
        
        past_time = int((datetime.now() - timedelta(hours=1)).timestamp())
        future_time = int((datetime.now() + timedelta(hours=1)).timestamp())
        
        # Act
        self.blacklist.add_to_blacklist(expired_jti, past_time)
        self.blacklist.add_to_blacklist(valid_jti, future_time)
        
        # Adicionar um novo token deve acionar a limpeza de expirados
        self.blacklist.add_to_blacklist("trigger_cleanup", future_time) 
        
        # Assert
        assert expired_jti not in self.blacklist._blacklist  # Token expirado deve ser removido
        assert valid_jti in self.blacklist._blacklist  # Token válido deve permanecer


class TestAuthManager:
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.app = Flask(__name__)
        self.app.config['JWT_SECRET_KEY'] = 'test-secret-key'
        self.app.config['TESTING'] = True
        self.auth_manager = AuthManager(self.app)
    
    def test_token_creation(self):
        """Testa criação de token de acesso."""
        # Act
        token = self.auth_manager.create_token("test_user", ROLE_ADMIN)
        
        # Assert
        decoded = decode_token(token)
        assert decoded["sub"]["user"] == "test_user"
        assert decoded["sub"]["role"] == ROLE_ADMIN

    def test_refresh_token_creation(self):
        """Testa criação de refresh token."""
        # Act
        token = self.auth_manager.create_refresh_token("test_user", ROLE_OPERATOR)
        
        # Assert
        decoded = decode_token(token)
        assert decoded["sub"]["user"] == "test_user"
        assert decoded["sub"]["role"] == ROLE_OPERATOR
        assert decoded["type"] == "refresh"

    def test_password_hashing(self):
        """Testa hash e verificação de senha."""
        # Arrange
        password = "s3cur3_passw0rd!"
        
        # Act
        hashed = self.auth_manager.hash_password(password)
        
        # Assert
        assert password != hashed  # O hash não deve ser igual à senha original
        assert self.auth_manager.verify_password(password, hashed) == True
        assert self.auth_manager.verify_password("wrong_password", hashed) == False

    def test_role_authorization(self):
        """Testa verificação de autorização baseada em roles."""
        # Test cases
        assert self.auth_manager.is_role_authorized(ROLE_ADMIN, ROLE_ADMIN) == True
        assert self.auth_manager.is_role_authorized([ROLE_ADMIN, ROLE_OPERATOR], ROLE_OPERATOR) == True
        assert self.auth_manager.is_role_authorized([ROLE_ADMIN, ROLE_OPERATOR], ROLE_VIEWER) == False
        assert self.auth_manager.is_role_authorized([ROLE_ADMIN, ROLE_OPERATOR, ROLE_VIEWER], ROLE_VIEWER) == True


class TestJWTIntegration:
    """
    Testes de integração do JWT com a aplicação Flask.
    Requer flask_jwt_extended completamente inicializado.
    """
    @pytest.fixture
    def client(self):
        """Cria um cliente de teste Flask."""
        app = Flask(__name__)
        app.config['JWT_SECRET_KEY'] = 'test-integration-key'
        app.config['TESTING'] = True
        
        auth_manager = AuthManager(app)
        
        # Adicionar rota de teste protegida por JWT
        @app.route('/protected_admin', methods=['GET'])
        @jwt_required()
        def protected_admin():
            identity = get_jwt_identity()
            if identity.get('role') != ROLE_ADMIN:
                return {'error': 'Acesso negado'}, 403
            return {'message': f'Olá {identity.get("user")}!'}, 200
        
        @app.route('/login', methods=['POST'])
        def login():
            data = request.json
            username = data.get('username')
            password = data.get('password')
            
            # Mock de autenticação
            if username == 'admin' and password == 'admin123':
                access_token = auth_manager.create_token(username, ROLE_ADMIN)
                refresh_token = auth_manager.create_refresh_token(username, ROLE_ADMIN)
                return {'access_token': access_token, 'refresh_token': refresh_token}, 200
            
            elif username == 'viewer' and password == 'viewer123':
                access_token = auth_manager.create_token(username, ROLE_VIEWER)
                refresh_token = auth_manager.create_refresh_token(username, ROLE_VIEWER)
                return {'access_token': access_token, 'refresh_token': refresh_token}, 200
            
            return {'error': 'Credenciais inválidas'}, 401
        
        return app.test_client()

    def test_jwt_protected_endpoint(self, client):
        """Testa acesso a endpoint protegido por JWT."""
        # Arrange - Criar token para admin
        with client.application.app_context():
            token = create_access_token(
                identity={'user': 'admin_test', 'role': ROLE_ADMIN}
            )
        
        # Act - Acessar endpoint protegido com token
        response = client.get(
            '/protected_admin',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Olá admin_test!'

    def test_jwt_protected_endpoint_unauthorized_role(self, client):
        """Testa acesso negado por role inadequado."""
        # Arrange - Criar token para viewer
        with client.application.app_context():
            token = create_access_token(
                identity={'user': 'viewer_test', 'role': ROLE_VIEWER}
            )
        
        # Act - Tentar acessar endpoint admin com token viewer
        response = client.get(
            '/protected_admin',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # Assert
        assert response.status_code == 403
        data = json.loads(response.data)
        assert 'error' in data


if __name__ == '__main__':
    pytest.main(['-v', __file__])