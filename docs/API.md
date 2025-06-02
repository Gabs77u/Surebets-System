# 📚 API Documentation - Surebets System

## Introdução

Esta documentação descreve os principais endpoints das APIs do sistema Surebets, incluindo autenticação JWT avançada, validação rigorosa, sistema de roles e permissões, e proteções de segurança implementadas.

---

## 🔐 Autenticação (JWT) - Sistema Avançado

### Login com Validação Pydantic
- **POST /api/auth/login**
  - Descrição: Realiza login com validação rigorosa e retorna tokens JWT.
  - Validação: Schemas Pydantic para sanitização e proteção contra ataques
  - Body: 
    ```json
    { 
      "username": "string (3-50 chars, alphanumeric)", 
      "password": "string (6-128 chars)", 
      "use_cookie": false 
    }
    ```
  - Resposta de Sucesso:
    ```json
    {
      "access_token": "jwt-token",
      "refresh_token": "jwt-refresh-token",
      "role": "admin|operator|viewer",
      "permissions": {
        "can_manage_users": true,
        "can_delete_data": true,
        "can_configure_system": true,
        "can_manage_odds": true,
        "can_place_bets": true,
        "can_view_reports": true,
        "can_view_dashboard": true
      },
      "expires_in": 3600
    }
    ```
  - Proteções: SQL Injection, XSS, CSRF, Rate Limiting

### Refresh Token
- **POST /api/auth/refresh**
  - Descrição: Renova access token usando refresh token.
  - Header: `Authorization: Bearer <refresh_token>`
  - Body (opcional): `{ "use_cookie": false }`
  - Resposta: Novo access token com permissões atualizadas

### Logout Seguro
- **POST /api/auth/logout**
  - Descrição: Invalida token JWT (adiciona à blacklist).
  - Header: `Authorization: Bearer <access_token>`
  - Body (opcional): `{ "use_cookie": false }`
  - Funcionalidade: Token é adicionado à blacklist (Redis ou em memória)

### Verificação de Token
- **GET /api/auth/verify**
  - Descrição: Verifica validade do token e retorna informações do usuário.
  - Header: `Authorization: Bearer <access_token>`
  - Resposta:
    ```json
    {
      "authenticated": true,
      "user": "admin",
      "role": "admin",
      "permissions": {...},
      "expires_at": "2023-06-01T15:30:00.000Z",
      "remaining_seconds": 3540
    }
    ```

### Gestão de Tokens (Admin)
- **GET /api/auth/token-status** (Admin apenas)
  - Descrição: Status da blacklist de tokens
- **POST /api/auth/revoke-all/<username>** (Admin apenas)
  - Descrição: Revoga todos os tokens de um usuário
- **GET /api/auth/roles** (Admin apenas)
  - Descrição: Informações sobre roles e permissões disponíveis

---

## 🎭 Sistema de Roles e Permissões

### Roles Disponíveis
- **admin**: Acesso total ao sistema
- **operator**: Pode operar apostas e gerenciar alertas  
- **viewer**: Apenas visualização

### Permissões Granulares
```json
{
  "can_manage_users": "Gerenciar usuários do sistema",
  "can_delete_data": "Deletar dados do sistema", 
  "can_configure_system": "Configurar parâmetros do sistema",
  "can_manage_odds": "Gerenciar odds e apostas",
  "can_place_bets": "Realizar apostas",
  "can_view_reports": "Visualizar relatórios",
  "can_view_dashboard": "Acessar dashboard"
}
```

### Endpoints por Role
- **Admin**: `/api/admin/*`
- **Operator**: `/api/operator/*`
- **Viewer**: `/api/user/*`

---

## 📊 Dashboard com Autorização

### Dashboard Administrativo (Admin)
- **GET /api/admin/dashboard**
  - Descrição: Dashboard completo com dados sensíveis
  - Permissão: Apenas admin
  - Resposta: Estatísticas completas, usuários, surebets recentes

### Dashboard Operacional (Admin + Operator)
- **GET /api/operator/dashboard**
  - Descrição: Dashboard para operadores
  - Permissão: Admin e Operator
  - Resposta: Surebets ativos, estatísticas operacionais

### Dashboard Usuário (Todos)
- **GET /api/user/dashboard**
  - Descrição: Dashboard básico para todos os usuários
  - Permissão: Qualquer usuário autenticado
  - Resposta: Estatísticas básicas de oportunidades

### Oportunidades com Validação
- **POST /api/opportunities**
  - Descrição: Lista oportunidades com validação de parâmetros
  - Validação: Schema Pydantic para parâmetros de busca
  - Parâmetros validados: `?query=string&page=1&limit=20&sport=soccer`
  - Body:
    ```json
    {
      "sports": ["soccer", "basketball"],
      "min_profit": 2.0,
      "bookmakers": ["bet365", "pinnacle"],
      "search": "termo_busca"
    }
    ```
  - Proteções: Sanitização XSS, validação de range

---

## ⚙️ Administração com Segurança Rigorosa

### Gestão de Usuários (Admin)
- **GET /api/admin/users**
  - Descrição: Lista usuários do sistema
  - Permissão: Admin apenas
- **POST /api/admin/users**
  - Descrição: Cria/atualiza usuário com validação rigorosa
  - Validação: Schema Pydantic UserCreateSchema
  - Body:
    ```json
    {
      "username": "string (3-50 chars, pattern: ^[a-zA-Z0-9_.-]+$)",
      "password": "string (8+ chars, força validada)",
      "email": "valid_email@domain.com",
      "role": "admin|operator|viewer"
    }
    ```
  - Proteções: Força da senha, sanitização, validação de email
- **DELETE /api/admin/users/<user_id>**
  - Descrição: Remove usuário (Admin apenas)

### Inserção de Apostas com Validação
- **POST /api/admin/insert-bet**
  - Descrição: Insere aposta com validação Pydantic
  - Validação: Schema BetInsertSchema
  - Headers: CSRF Token obrigatório
  - Body:
    ```json
    {
      "event": "string (3-200 chars, sanitizado)",
      "market": "string (2-100 chars, sanitizado)", 
      "selection": "string (2-100 chars, sanitizado)",
      "odd": "float (1.0 < odd <= 1000.0)",
      "bookmaker": "string (2-50 chars, sanitizado)"
    }
    ```
  - Proteções: Sanitização XSS, validação de odd, CSRF

### Configurações Seguras
- **GET /api/admin/settings**
  - Descrição: Configurações do sistema (dados seguros apenas)
- **POST /api/admin/settings**
  - Descrição: Atualiza configurações com validação

---

## 🔒 Recursos de Segurança Implementados

### Validação de Entrada
- **Pydantic Schemas**: Validação rigorosa de todos os inputs
- **Sanitização XSS**: Remoção automática de scripts maliciosos
- **Proteção SQL Injection**: Detecção de padrões suspeitos
- **CSRF Protection**: Tokens CSRF obrigatórios em operações sensíveis

### Headers de Segurança
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self'
```

### Rate Limiting e Monitoramento
- Limite de requisições por IP
- Logging de eventos de segurança
- Detecção de ataques automatizada
- Blacklist de tokens revogados

---

## 🏦 Adaptadores de Bookmakers

### Lista de Adaptadores
- **GET /api/adapters/list**
  - Descrição: Lista adaptadores disponíveis e status

### Atualização de Dados
- **POST /api/adapters/refresh**
  - Descrição: Força atualização dos dados dos bookmakers
  - Proteções: Rate limiting, validação de origem

---

## 🩺 Health & Metrics

### Health Check Avançado
- **GET /health**
  - Descrição: Health check com status detalhado
  - Resposta:
    ```json
    {
      "status": "ok",
      "database": "connected",
      "redis": "connected", 
      "adapters": "operational",
      "timestamp": "2023-06-01T12:00:00Z"
    }
    ```

### Métricas de Monitoramento
- **GET /metrics**
  - Descrição: Métricas Prometheus para monitoramento
  - Inclui: Requests, errors, response times, active tokens

---

## 🔒 Autenticação por Cookies (SPA)

Para Single Page Applications, o sistema suporta autenticação via cookies seguros:

```javascript
// Login com cookies
fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'user',
    password: 'pass',
    use_cookie: true
  }),
  credentials: 'include'
});
```

---

## 📋 Códigos de Status

- **200**: Sucesso
- **400**: Dados inválidos / Erro de validação
- **401**: Token expirado / Credenciais inválidas
- **403**: Permissão insuficiente
- **422**: Erro de validação Pydantic
- **429**: Rate limit excedido
- **500**: Erro interno do servidor

---

## 🛡️ Exemplos de Proteções Ativas

### Tentativa de SQL Injection
```bash
# Request malicioso (bloqueado)
curl -X POST /api/auth/login \
  -d '{"username":"admin\"; DROP TABLE users; --","password":"test"}'
# Resposta: 400 - "Conteúdo suspeito detectado"
```

### Tentativa de XSS
```bash
# Request malicioso (sanitizado)
curl -X POST /api/admin/insert-bet \
  -d '{"event":"<script>alert(\"xss\")</script>Game",...}'
# Evento é sanitizado automaticamente
```

---

## 📖 Exemplos de Uso Completos

### Fluxo de Autenticação Completo
```bash
# 1. Login
LOGIN_RESPONSE=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
REFRESH_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.refresh_token')

# 2. Acessar recurso protegido
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://localhost:5000/api/admin/dashboard

# 3. Renovar token
NEW_TOKEN=$(curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer $REFRESH_TOKEN" | jq -r '.access_token')

# 4. Logout seguro
curl -X POST http://localhost:5000/api/auth/logout \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

## 🔗 Links Relacionados

- **[Guia de Integração JWT Frontend](JWT_FRONTEND_INTEGRACAO.md)**
- **[Documentação de Segurança](SECURITY.md)**
- **[Guia de Desenvolvimento](DESENVOLVIMENTO_COMPLETO.md)**
