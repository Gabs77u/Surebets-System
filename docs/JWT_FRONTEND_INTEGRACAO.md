# Guia de Integração JWT com Frontend

Este documento descreve como integrar o sistema de autenticação JWT do Surebets Hunter Pro com aplicações frontend.

## Índice

1. [Visão Geral](#visão-geral)
2. [Endpoints de Autenticação](#endpoints-de-autenticação)
3. [Fluxo de Autenticação](#fluxo-de-autenticação)
4. [Integração com React](#integração-com-react)
5. [Integração com Vue.js](#integração-com-vuejs)
6. [Gerenciamento de Roles e Permissões](#gerenciamento-de-roles-e-permissões)
7. [Lidando com Expiração de Token](#lidando-com-expiração-de-token)
8. [Segurança](#segurança)

## Visão Geral

O Surebets Hunter Pro implementa autenticação baseada em JWT (JSON Web Tokens) seguindo o padrão OAuth2. O sistema oferece:

- Autenticação baseada em token
- Refresh tokens para renovação automática
- Blacklist de tokens revogados
- Sistema avançado de roles (admin, operador, viewer)
- Permissões granulares para controle de acesso
- Suporte a cookies seguros para SPAs

## Endpoints de Autenticação

### Login
- **URL**: `/api/auth/login`
- **Método**: `POST`
- **Payload**:
```json
{
  "username": "seu_usuario",
  "password": "sua_senha",
  "use_cookie": false
}
```
- **Resposta**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "admin",
  "permissions": {
    "can_manage_users": true,
    "can_delete_data": true
  },
  "expires_in": 3600
}
```

### Refresh Token
- **URL**: `/api/auth/refresh`
- **Método**: `POST`
- **Headers**: `Authorization: Bearer {refresh_token}`
- **Payload** (opcional):
```json
{
  "use_cookie": false
}
```
- **Resposta**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "admin",
  "permissions": {
    "can_manage_users": true,
    "can_delete_data": true
  },
  "expires_in": 3600
}
```

### Logout
- **URL**: `/api/auth/logout`
- **Método**: `POST`
- **Headers**: `Authorization: Bearer {access_token}`
- **Payload** (opcional):
```json
{
  "use_cookie": false
}
```
- **Resposta**:
```json
{
  "status": "success",
  "message": "Logout realizado com sucesso"
}
```

### Verificar Token
- **URL**: `/api/auth/verify`
- **Método**: `GET`
- **Headers**: `Authorization: Bearer {access_token}`
- **Resposta**:
```json
{
  "authenticated": true,
  "user": "admin",
  "role": "admin",
  "permissions": {
    "can_manage_users": true,
    "can_delete_data": true
  },
  "expires_at": "2023-06-01T15:30:00.000Z",
  "remaining_seconds": 3540
}
```

## Fluxo de Autenticação

1. **Login**: Chamar `/api/auth/login` para obter `access_token` e `refresh_token`
2. **Usar API**: Incluir o `access_token` no header `Authorization: Bearer {token}` para acessar endpoints protegidos
3. **Renovar Token**: Quando o `access_token` expirar, usar o `refresh_token` para obter um novo
4. **Logout**: Chamar `/api/auth/logout` para revogar o token atual

## Integração com React

Exemplo de integração com React usando um contexto de autenticação:

```jsx
// AuthContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'https://api.surebets-hunter.com';
const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Verificar se já existe um token armazenado
    const token = localStorage.getItem('access_token');
    if (token) {
      verifyToken();
    } else {
      setLoading(false);
    }
  }, []);
  
  // Configurar interceptor para renovar token automaticamente
  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      response => response,
      async (error) => {
        const originalRequest = error.config;
        
        // Se o erro for 401 e não for uma tentativa de refresh, tentar renovar o token
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            await refreshToken();
            originalRequest.headers.Authorization = `Bearer ${localStorage.getItem('access_token')}`;
            return axios(originalRequest);
          } catch (refreshError) {
            // Se falhar o refresh, redirecionar para login
            logout();
            return Promise.reject(refreshError);
          }
        }
        
        return Promise.reject(error);
      }
    );
    
    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, []);
  
  const login = async (username, password) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API_URL}/api/auth/login`, {
        username,
        password
      });
      
      const { access_token, refresh_token, role, permissions } = response.data;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      setUser({
        username,
        role,
        permissions
      });
      
      // Configurar axios para usar token em todas as requisições
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      return true;
    } catch (error) {
      console.error('Erro no login:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };
  
  const logout = async () => {
    try {
      // Revogar token no servidor
      const token = localStorage.getItem('access_token');
      if (token) {
        await axios.post(
          `${API_URL}/api/auth/logout`,
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );
      }
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
    } finally {
      // Limpar dados locais
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      delete axios.defaults.headers.common['Authorization'];
      setUser(null);
    }
  };
  
  const refreshToken = async () => {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) {
      throw new Error('No refresh token available');
    }
    
    const response = await axios.post(
      `${API_URL}/api/auth/refresh`,
      {},
      { headers: { Authorization: `Bearer ${refresh}` } }
    );
    
    const { access_token } = response.data;
    localStorage.setItem('access_token', access_token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    
    return access_token;
  };
  
  const verifyToken = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      if (!token) {
        setLoading(false);
        return false;
      }
      
      const response = await axios.get(
        `${API_URL}/api/auth/verify`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.authenticated) {
        setUser({
          username: response.data.user,
          role: response.data.role,
          permissions: response.data.permissions
        });
        
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        return true;
      } else {
        // Token inválido, tentar refresh
        try {
          await refreshToken();
          return verifyToken();
        } catch (refreshError) {
          logout();
          return false;
        }
      }
    } catch (error) {
      console.error('Erro ao verificar token:', error);
      logout();
      return false;
    } finally {
      setLoading(false);
    }
  };
  
  const hasPermission = (permission) => {
    if (!user || !user.permissions) return false;
    return user.permissions[permission] === true;
  };
  
  const value = {
    user,
    loading,
    login,
    logout,
    refreshToken,
    hasPermission
  };
  
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
```

**Uso em componentes:**

```jsx
// Login.js
import React, { useState } from 'react';
import { useAuth } from './AuthContext';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, loading } = useAuth();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    const success = await login(username, password);
    if (!success) {
      setError('Credenciais inválidas');
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <h2>Login</h2>
      {error && <div className="error">{error}</div>}
      <div>
        <label>Usuário</label>
        <input 
          type="text" 
          value={username} 
          onChange={(e) => setUsername(e.target.value)} 
          required 
        />
      </div>
      <div>
        <label>Senha</label>
        <input 
          type="password" 
          value={password} 
          onChange={(e) => setPassword(e.target.value)} 
          required 
        />
      </div>
      <button type="submit" disabled={loading}>
        {loading ? 'Carregando...' : 'Entrar'}
      </button>
    </form>
  );
}

// PrivateRoute.js
function PrivateRoute({ children, requiredPermission }) {
  const { user, loading } = useAuth();
  const navigate = useNavigate();
  
  useEffect(() => {
    if (!loading && !user) {
      navigate('/login');
    }
    
    if (user && requiredPermission && !user.permissions[requiredPermission]) {
      navigate('/unauthorized');
    }
  }, [user, loading, navigate, requiredPermission]);
  
  if (loading) {
    return <div>Carregando...</div>;
  }
  
  return user ? children : null;
}
```

## Integração com Vue.js

Exemplo de integração com Vue.js:

```js
// auth.js
import axios from 'axios';

const API_URL = 'https://api.surebets-hunter.com';

export default {
  namespaced: true,
  
  state: {
    user: null,
    token: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    loading: false
  },
  
  mutations: {
    SET_USER(state, user) {
      state.user = user;
    },
    SET_TOKENS(state, { accessToken, refreshToken }) {
      state.token = accessToken;
      state.refreshToken = refreshToken;
      
      if (accessToken) {
        localStorage.setItem('access_token', accessToken);
        axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
      } else {
        localStorage.removeItem('access_token');
        delete axios.defaults.headers.common['Authorization'];
      }
      
      if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken);
      } else {
        localStorage.removeItem('refresh_token');
      }
    },
    SET_LOADING(state, loading) {
      state.loading = loading;
    }
  },
  
  actions: {
    async login({ commit }, { username, password }) {
      try {
        commit('SET_LOADING', true);
        
        const response = await axios.post(`${API_URL}/api/auth/login`, {
          username,
          password
        });
        
        const { access_token, refresh_token, role, permissions } = response.data;
        
        commit('SET_TOKENS', { 
          accessToken: access_token, 
          refreshToken: refresh_token 
        });
        
        commit('SET_USER', {
          username,
          role,
          permissions
        });
        
        return true;
      } catch (error) {
        console.error('Erro no login:', error);
        return false;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async logout({ commit, state }) {
      try {
        if (state.token) {
          await axios.post(
            `${API_URL}/api/auth/logout`,
            {},
            { headers: { Authorization: `Bearer ${state.token}` } }
          );
        }
      } catch (error) {
        console.error('Erro ao fazer logout:', error);
      } finally {
        commit('SET_TOKENS', { accessToken: null, refreshToken: null });
        commit('SET_USER', null);
      }
    },
    
    async refreshToken({ commit, state }) {
      if (!state.refreshToken) {
        throw new Error('No refresh token available');
      }
      
      try {
        const response = await axios.post(
          `${API_URL}/api/auth/refresh`,
          {},
          { headers: { Authorization: `Bearer ${state.refreshToken}` } }
        );
        
        const { access_token } = response.data;
        
        commit('SET_TOKENS', { 
          accessToken: access_token, 
          refreshToken: state.refreshToken 
        });
        
        return access_token;
      } catch (error) {
        commit('SET_TOKENS', { accessToken: null, refreshToken: null });
        commit('SET_USER', null);
        throw error;
      }
    },
    
    async verifyToken({ commit, state, dispatch }) {
      if (!state.token) return false;
      
      try {
        commit('SET_LOADING', true);
        
        const response = await axios.get(
          `${API_URL}/api/auth/verify`,
          { headers: { Authorization: `Bearer ${state.token}` } }
        );
        
        if (response.data.authenticated) {
          commit('SET_USER', {
            username: response.data.user,
            role: response.data.role,
            permissions: response.data.permissions
          });
          return true;
        } else {
          // Token inválido, tentar refresh
          try {
            await dispatch('refreshToken');
            return dispatch('verifyToken');
          } catch (refreshError) {
            dispatch('logout');
            return false;
          }
        }
      } catch (error) {
        console.error('Erro ao verificar token:', error);
        dispatch('logout');
        return false;
      } finally {
        commit('SET_LOADING', false);
      }
    }
  },
  
  getters: {
    isAuthenticated: state => !!state.user,
    hasPermission: state => permission => {
      if (!state.user || !state.user.permissions) return false;
      return state.user.permissions[permission] === true;
    },
    userRole: state => state.user ? state.user.role : null
  }
};

// main.js
import { createApp } from 'vue';
import { createStore } from 'vuex';
import axios from 'axios';
import App from './App.vue';
import router from './router';
import auth from './auth';

const store = createStore({
  modules: {
    auth
  }
});

// Configurar interceptor para refresh token
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status !== 401) {
      return Promise.reject(error);
    }
    
    const originalRequest = error.config;
    if (originalRequest._retry) {
      return Promise.reject(error);
    }
    
    originalRequest._retry = true;
    
    try {
      await store.dispatch('auth/refreshToken');
      return axios(originalRequest);
    } catch (refreshError) {
      router.push('/login');
      return Promise.reject(refreshError);
    }
  }
);

const app = createApp(App);
app.use(store);
app.use(router);
app.mount('#app');
```

## Gerenciamento de Roles e Permissões

O sistema implementa um controle de acesso baseado em roles e permissões granulares:

| Role | Descrição |
|------|-----------|
| `admin` | Acesso completo ao sistema |
| `operator` | Pode operar apostas e gerenciar alertas |
| `viewer` | Apenas visualização |

Cada role possui um conjunto de permissões que determinam o que o usuário pode fazer:

```json
{
  "admin": {
    "can_manage_users": true,
    "can_delete_data": true,
    "can_configure_system": true,
    "can_manage_odds": true,
    "can_place_bets": true,
    "can_view_reports": true,
    "can_view_dashboard": true
  },
  "operator": {
    "can_manage_users": false,
    "can_delete_data": false,
    "can_configure_system": false,
    "can_manage_odds": true,
    "can_place_bets": true,
    "can_view_reports": true,
    "can_view_dashboard": true
  },
  "viewer": {
    "can_manage_users": false,
    "can_delete_data": false,
    "can_configure_system": false,
    "can_manage_odds": false,
    "can_place_bets": false,
    "can_view_reports": true,
    "can_view_dashboard": true
  }
}
```

No frontend, implemente verificações baseadas nas permissões:

```jsx
// React
function Button({ permission, children, ...props }) {
  const { hasPermission } = useAuth();
  
  if (permission && !hasPermission(permission)) {
    return null;
  }
  
  return <button {...props}>{children}</button>;
}

// Vue
<template>
  <button v-if="!permission || $store.getters['auth/hasPermission'](permission)">
    <slot></slot>
  </button>
</template>
```

## Lidando com Expiração de Token

Os access tokens são configurados para expirar após 60 minutos por padrão. O frontend deve implementar:

1. **Refresh Automático**: Usar interceptores para detectar erros 401 e renovar o token
2. **Verificação Periódica**: Em aplicações que ficam abertas por longos períodos, verifique o status do token regularmente
3. **Logout Automático**: Após inatividade prolongada, fazer logout automático

```js
// Verificação periódica
function startTokenRefreshTimer() {
  const FIFTEEN_MINUTES = 15 * 60 * 1000;
  
  return setInterval(async () => {
    try {
      const response = await fetch('/api/auth/verify', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      const data = await response.json();
      
      // Se o token vai expirar em menos de 15 minutos, renovar
      if (data.authenticated && data.remaining_seconds < 900) {
        await refreshToken();
      }
    } catch (error) {
      console.error('Erro na verificação periódica do token:', error);
    }
  }, FIFTEEN_MINUTES);
}
```

## Segurança

Para garantir a segurança do sistema de autenticação:

1. **Sempre use HTTPS** em produção
2. **Não armazene tokens em localStorage** em aplicações com requisitos de segurança críticos (prefira cookies HttpOnly)
3. **Implemente proteção contra CSRF** utilizando o modo `use_cookie: true` e incluindo o header `X-CSRF-Token`
4. **Revogue tokens** ao fazer logout
5. **Implemente logout automático** após inatividade
6. **Limpe tokens** quando o usuário fechar a aplicação

Para maior segurança, utilize o modo baseado em cookies:

```js
// Login com cookies
async function loginWithCookies(username, password) {
  await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username,
      password,
      use_cookie: true
    }),
    credentials: 'include' // Importante: incluir cookies na requisição
  });
}

// Logout com cookies
async function logoutWithCookies() {
  await fetch('/api/auth/logout', {
    method: 'POST',
    body: JSON.stringify({ use_cookie: true }),
    credentials: 'include'
  });
}
```