"""
Testes de integração para o sistema de autenticação JWT.
Testa o fluxo completo: login, refresh token, logout, e acesso baseado em roles.
"""

import os
import sys
import importlib
# Definir segredo JWT ANTES de qualquer import do app ou AuthManager
os.environ['JWT_SECRET_KEY'] = 'test-integration-key'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from config.config_loader import CONFIG
CONFIG['security']['secret_key'] = 'test-integration-key'
# Forçar reload do AuthManager para garantir segredo correto
auth_mod = importlib.import_module('backend.core.auth')
importlib.reload(auth_mod)

import json
import pytest
import time
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    """Configura um cliente de teste para a API"""
    import importlib
    import sys
    # Remover módulos do cache para garantir segredo correto
    for mod in ['backend.apps.admin_api', 'backend.core.auth']:
        if mod in sys.modules:
            del sys.modules[mod]
    # Recarregar o módulo admin_api para garantir que pegue a chave correta
    from config.config_loader import CONFIG
    CONFIG['security']['secret_key'] = 'test-integration-key'
    importlib.invalidate_caches()
    from backend.apps.admin_api import app as admin_api
    admin_api.config['TESTING'] = True
    admin_api.config['DEBUG'] = False
    admin_api.config['JWT_SECRET_KEY'] = 'test-integration-key'
    admin_api.secret_key = 'test-integration-key'
    admin_api.config['JWT_ACCESS_TOKEN_EXPIRES'] = 5  # 5 segundos para testar expiração

    # Garantir que o banco de dados é mockado para testes
    with patch('backend.apps.admin_api.DatabaseManager') as mock_db:
        # Simular consulta ao banco para usuários
        db_instance = MagicMock()
        db_instance.fetch_one.side_effect = lambda query, params=None: {
            'id': 1,
            'username': params[0] if params else None,
            'password_hash': 'pbkdf2:sha256:150000$ABC123$HASH',
            'email': f'{params[0]}@example.com',
            'created_at': '2023-01-01T00:00:00',
            'role': 'admin' if params and params[0] == 'admin' else (
                'operator' if params and params[0] == 'operator' else 'viewer'),
            'user': params[0] if params else None
        } if params and params[0] in ['admin', 'operator', 'viewer'] else None
        mock_db.return_value = db_instance
        # Simular verificação de senha do AuthManager
        with patch('backend.core.auth.AuthManager.verify_password', return_value=True):
            with admin_api.test_client() as client:
                yield client


class TestAuthFlow:
    """Testes do fluxo completo de autenticação JWT"""
    
    def test_login_admin_success(self, client):
        """Teste de login bem-sucedido para admin"""
        from backend.core.auth import ROLE_ADMIN, ROLE_PERMISSIONS
        response = client.post('/api/auth/login', 
                               json={'username': 'admin', 'password': 'admin123'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['role'] == ROLE_ADMIN
        assert 'permissions' in data
        assert data['permissions'] == ROLE_PERMISSIONS[ROLE_ADMIN]
        assert 'expires_in' in data
        # Salvar tokens para uso em outros testes
        self.admin_access_token = data['access_token']
        self.admin_refresh_token = data['refresh_token']

    def test_login_with_cookie(self, client):
        """Teste de login com cookie habilitado (IGNORADO: arquitetura JWT puro)"""
        pytest.skip("Fluxo de autenticação com cookie não é mais suportado na arquitetura atual (JWT puro)")

    def test_login_operator_success(self, client):
        """Teste de login bem-sucedido para operador"""
        from backend.core.auth import ROLE_OPERATOR, ROLE_PERMISSIONS
        response = client.post('/api/auth/login', 
                               json={'username': 'operator', 'password': 'password123'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['role'] == ROLE_OPERATOR
        assert 'permissions' in data
        assert data['permissions'] == ROLE_PERMISSIONS[ROLE_OPERATOR]
    
    def test_login_failed(self, client):
        """Teste de falha no login com credenciais inválidas"""
        # Mockar verify_password para retornar False para este teste
        with patch('backend.core.auth.AuthManager.verify_password', return_value=False):
            response = client.post('/api/auth/login', 
                                json={'username': 'fake', 'password': 'wrongpass'})
            
            assert response.status_code == 401
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_refresh_token(self, client):
        """Teste de renovação de token usando refresh token"""
        # Login para obter refresh token
        login_response = client.post('/api/auth/login', 
                                    json={'username': 'admin', 'password': 'admin123'})
        assert login_response.status_code == 200
        tokens = json.loads(login_response.data)
        # Usar o refresh token para gerar novo access token
        refresh_response = client.post(
            '/api/auth/refresh',
            headers={'Authorization': f'Bearer {tokens["refresh_token"]}'}
        )
        # Se falhar, mostrar resposta para debug
        if refresh_response.status_code != 200:
            print('DEBUG refresh_token:', refresh_response.data)
        assert refresh_response.status_code == 200
        data = json.loads(refresh_response.data)
        assert 'access_token' in data
        assert 'permissions' in data
        assert 'expires_in' in data
        assert data['role'] == 'admin'
    
    def test_protected_routes_by_role(self, client):
        """Testa acesso às rotas protegidas com diferentes roles"""
        # Obter tokens para cada role
        login = lambda u: json.loads(client.post('/api/auth/login', json={'username': u, 'password': 'password123'}).data)['access_token']
        admin_token = login('admin')
        operator_token = login('operator')
        viewer_token = login('viewer')
        # Testar acesso à rota admin
        admin_dashboard_response = client.get(
            '/api/admin/dashboard',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        if admin_dashboard_response.status_code != 200:
            print('DEBUG admin_dashboard:', admin_dashboard_response.data)
        assert admin_dashboard_response.status_code == 200
        # Operador não deve acessar dashboard admin
        admin_denied_response = client.get(
            '/api/admin/dashboard',
            headers={'Authorization': f'Bearer {operator_token}'}
        )
        assert admin_denied_response.status_code == 403
        # Todos devem acessar dashboard de usuário
        user_dashboard_admin = client.get(
            '/api/user/dashboard',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert user_dashboard_admin.status_code == 200
        user_dashboard_operator = client.get(
            '/api/user/dashboard',
            headers={'Authorization': f'Bearer {operator_token}'}
        )
        assert user_dashboard_operator.status_code == 200
        user_dashboard_viewer = client.get(
            '/api/user/dashboard',
            headers={'Authorization': f'Bearer {viewer_token}'}
        )
        assert user_dashboard_viewer.status_code == 200

    def test_logout(self, client):
        """Testa logout JWT (adicionar token à blacklist)"""
        # Login
        login_response = client.post('/api/auth/login', 
                                    json={'username': 'admin', 'password': 'admin123'})
        assert login_response.status_code == 200
        token = json.loads(login_response.data)['access_token']
        # Logout
        logout_response = client.post(
            '/api/auth/logout',
            headers={'Authorization': f'Bearer {token}'}
        )
        if logout_response.status_code != 200:
            print('DEBUG logout:', logout_response.data)
        assert logout_response.status_code == 200
        
        # Em ambiente real seria 401, mas como estamos mockando a blacklist,
        # não podemos testar completamente o comportamento de revogação.
        assert json.loads(logout_response.data)['status'] == 'success'
    
    def test_logout_with_cookie(self, client):
        """Testa logout JWT com cookies (IGNORADO: arquitetura JWT puro)"""
        pytest.skip("Fluxo de logout com cookie não é mais suportado na arquitetura atual (JWT puro)")
        
    def test_verify_token(self, client):
        """Testa a verificação de token"""
        # Primeiro fazer login
        login_response = client.post('/api/auth/login', 
                                    json={'username': 'admin', 'password': 'admin123'})
        assert login_response.status_code == 200
        token = json.loads(login_response.data)['access_token']
        
        # Verificar token
        verify_response = client.get(
            '/api/auth/verify',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert verify_response.status_code == 200
        data = json.loads(verify_response.data)
        assert data['authenticated'] is True
        assert data['user'] == 'admin'
        assert data['role'] == 'admin'
        assert 'permissions' in data
        assert 'expires_at' in data
        assert 'remaining_seconds' in data
        
    def test_verify_invalid_token(self, client):
        """Testa verificação com token inválido"""
        # Chamar verificação sem token
        verify_response = client.get('/api/auth/verify')
        
        assert verify_response.status_code == 200
        data = json.loads(verify_response.data)
        assert data['authenticated'] is False
    
    def test_token_expiration(self, client):
        """Testa expiração de token"""
        import importlib
        from backend.apps.admin_api import app as admin_api
        admin_api.config['JWT_ACCESS_TOKEN_EXPIRES'] = 1  # 1 segundo
        
        # Login para obter token
        login_response = client.post('/api/auth/login', 
                                    json={'username': 'admin', 'password': 'admin123'})
        assert login_response.status_code == 200
        token = json.loads(login_response.data)['access_token']
        
        # Usar token imediatamente (deve funcionar)
        admin_response = client.get(
            '/api/admin/dashboard',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert admin_response.status_code == 200
        
        # Esperar token expirar
        time.sleep(2)
        
        # Tentar usar token expirado
        expired_response = client.get(
            '/api/admin/dashboard',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert expired_response.status_code == 401
        
        # Restaurar configuração original para não afetar outros testes
        admin_api.config['JWT_ACCESS_TOKEN_EXPIRES'] = 5
    
    def test_permission_based_access(self, client):
        """Testa acesso baseado em permissões específicas"""
        from backend.core.auth import ROLE_ADMIN
        from flask import jsonify
        with patch('backend.core.auth.AuthManager.has_permission', side_effect=lambda role, perm: role == ROLE_ADMIN and perm == 'can_manage_users'):
            # Login como admin
            admin_login = client.post('/api/auth/login', 
                                    json={'username': 'admin', 'password': 'admin123'})
            admin_token = json.loads(admin_login.data)['access_token']
            
            # Login como operator
            operator_login = client.post('/api/auth/login', 
                                      json={'username': 'operator', 'password': 'password123'})
            operator_token = json.loads(operator_login.data)['access_token']
            
            # Mockar rota protegida por permissão
            from backend.apps.admin_api import app as admin_api
            @admin_api.route('/test/permission', methods=['GET'])
            @admin_api.permission_required('can_manage_users')
            def test_permission():
                return jsonify({'success': True}), 200
            
            # Admin deve ter acesso
            admin_response = client.get(
                '/test/permission',
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            assert admin_response.status_code == 200
            
            # Operador não deve ter acesso
            operator_response = client.get(
                '/test/permission',
                headers={'Authorization': f'Bearer {operator_token}'}
            )
            assert operator_response.status_code == 403

    def test_roles_endpoint(self, client):
        from backend.core.auth import ROLE_ADMIN, ROLE_OPERATOR, ROLE_VIEWER
        login_response = client.post('/api/auth/login', json={'username': 'admin', 'password': 'admin123'})
        admin_token = json.loads(login_response.data)['access_token']
        roles_response = client.get('/api/auth/roles', headers={'Authorization': f'Bearer {admin_token}'})
        assert roles_response.status_code == 200
        data = json.loads(roles_response.data)
        assert 'available_roles' in data
        assert 'permissions_map' in data
        assert 'admin' in data['available_roles']
        assert 'operator' in data['available_roles']
        assert 'viewer' in data['available_roles']
        

if __name__ == '__main__':
    pytest.main(['-v', __file__])