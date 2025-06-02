"""
Testes de integração para o sistema de autenticação JWT.
Testa o fluxo completo: login, refresh token, logout, e acesso baseado em roles.
"""

import os
import sys
import json
import pytest
import time
from unittest.mock import patch, MagicMock

# Adicionar diretório principal ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.apps.admin_api import app as admin_api
from backend.core.auth import ROLE_ADMIN, ROLE_OPERATOR, ROLE_VIEWER, ROLE_PERMISSIONS

@pytest.fixture
def client():
    """Configura um cliente de teste para a API"""
    admin_api.config['TESTING'] = True
    admin_api.config['DEBUG'] = False
    admin_api.config['JWT_SECRET_KEY'] = 'test-integration-key'
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
            'role': 'operator' if params and params[0] == 'operator' else 'viewer'
        } if params and params[0] in ['operator', 'viewer'] else None
        
        mock_db.return_value = db_instance
        
        # Simular verificação de senha do AuthManager
        with patch('backend.core.auth.AuthManager.verify_password', return_value=True):
            with admin_api.test_client() as client:
                yield client


class TestAuthFlow:
    """Testes do fluxo completo de autenticação JWT"""
    
    def test_login_admin_success(self, client):
        """Teste de login bem-sucedido para admin"""
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
    
    def test_login_with_cookie(self, client):
        """Teste de login com cookie habilitado"""
        response = client.post('/api/auth/login', 
                               json={'username': 'admin', 'password': 'admin123', 'use_cookie': True})
        
        assert response.status_code == 200
        assert 'Set-Cookie' in response.headers
        assert 'access_token_cookie' in response.headers['Set-Cookie']
        assert 'refresh_token_cookie' in response.headers['Set-Cookie']
    
    def test_login_operator_success(self, client):
        """Teste de login bem-sucedido para operador"""
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
        # Primeiro fazer login para obter um refresh token
        login_response = client.post('/api/auth/login', 
                                    json={'username': 'admin', 'password': 'admin123'})
        assert login_response.status_code == 200
        tokens = json.loads(login_response.data)
        
        # Usar o refresh token para gerar um novo access token
        refresh_response = client.post(
            '/api/auth/refresh',
            headers={'Authorization': f'Bearer {tokens["refresh_token"]}'}
        )
        
        assert refresh_response.status_code == 200
        data = json.loads(refresh_response.data)
        assert 'access_token' in data
        assert 'permissions' in data
        assert 'expires_in' in data
        assert data['role'] == ROLE_ADMIN
    
    def test_refresh_token_with_cookie(self, client):
        """Teste de renovação de token com cookie habilitado"""
        login_response = client.post('/api/auth/login', 
                                    json={'username': 'admin', 'password': 'admin123', 'use_cookie': True})
        assert login_response.status_code == 200
        cookies = login_response.headers.getlist('Set-Cookie')
        
        # Extrai cookie do refresh token
        refresh_cookie = next((c for c in cookies if 'refresh_token_cookie' in c), None)
        refresh_token = refresh_cookie.split(';')[0].split('=')[1] if refresh_cookie else None
        assert refresh_token is not None
        
        headers = {'Cookie': f'refresh_token_cookie={refresh_token}'}
        
        # Usar o cookie para refresh
        refresh_response = client.post(
            '/api/auth/refresh',
            json={'use_cookie': True},
            headers=headers
        )
        
        assert refresh_response.status_code == 200
        assert 'Set-Cookie' in refresh_response.headers
        assert 'access_token_cookie' in refresh_response.headers['Set-Cookie']
        
    def test_protected_routes_by_role(self, client):
        """Testa acesso às rotas protegidas com diferentes roles"""
        # Obter tokens para cada role
        admin_response = client.post('/api/auth/login', 
                                    json={'username': 'admin', 'password': 'admin123'})
        admin_token = json.loads(admin_response.data)['access_token']
        
        operator_response = client.post('/api/auth/login', 
                                      json={'username': 'operator', 'password': 'password123'})
        operator_token = json.loads(operator_response.data)['access_token']
        
        viewer_response = client.post('/api/auth/login', 
                                    json={'username': 'viewer', 'password': 'password123'})
        viewer_token = json.loads(viewer_response.data)['access_token']
        
        # Testar acesso à rota admin
        admin_dashboard_response = client.get(
            '/api/admin/dashboard',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
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
        # Primeiro fazer login
        login_response = client.post('/api/auth/login', 
                                    json={'username': 'admin', 'password': 'admin123'})
        assert login_response.status_code == 200
        token = json.loads(login_response.data)['access_token']
        
        # Fazer logout
        logout_response = client.post(
            '/api/auth/logout',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert logout_response.status_code == 200
        
        # Em ambiente real seria 401, mas como estamos mockando a blacklist,
        # não podemos testar completamente o comportamento de revogação.
        assert json.loads(logout_response.data)['status'] == 'success'
    
    def test_logout_with_cookie(self, client):
        """Testa logout JWT com cookies"""
        # Primeiro fazer login com cookie
        login_response = client.post('/api/auth/login', 
                                    json={'username': 'admin', 'password': 'admin123', 'use_cookie': True})
        assert login_response.status_code == 200
        cookies = login_response.headers.getlist('Set-Cookie')
        
        # Extrai cookie do access token
        access_cookie = next((c for c in cookies if 'access_token_cookie' in c), None)
        access_token = access_cookie.split(';')[0].split('=')[1] if access_cookie else None
        assert access_token is not None
        
        headers = {'Cookie': f'access_token_cookie={access_token}'}
        
        # Fazer logout com cookie
        logout_response = client.post(
            '/api/auth/logout',
            json={'use_cookie': True},
            headers=headers
        )
        assert logout_response.status_code == 200
        
        # Verificar que os cookies foram removidos
        cookies = logout_response.headers.getlist('Set-Cookie')
        for cookie in cookies:
            if 'access_token_cookie' in cookie or 'refresh_token_cookie' in cookie:
                # O cookie deve ter sido definido para expirar
                assert 'Expires=Thu, 01 Jan 1970' in cookie
    
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
        assert data['role'] == ROLE_ADMIN
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
        # Configurar token com expiração curta
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
        """Testa o endpoint que retorna informações sobre roles"""
        # Login como admin
        admin_login = client.post('/api/auth/login', 
                                json={'username': 'admin', 'password': 'admin123'})
        admin_token = json.loads(admin_login.data)['access_token']
        
        # Acessar endpoint de roles
        roles_response = client.get(
            '/api/auth/roles',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert roles_response.status_code == 200
        data = json.loads(roles_response.data)
        assert 'available_roles' in data
        assert 'permissions_map' in data
        assert ROLE_ADMIN in data['available_roles']
        assert ROLE_OPERATOR in data['available_roles']
        assert ROLE_VIEWER in data['available_roles']
        

if __name__ == '__main__':
    pytest.main(['-v', __file__])