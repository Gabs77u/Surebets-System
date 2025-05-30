# 📚 API Documentation - Surebets System

## Introdução

Esta documentação descreve os principais endpoints das APIs do sistema Surebets, incluindo autenticação, dashboard, administração e integração com adaptadores de casas de apostas.

---

## 🔐 Autenticação (JWT)

- **POST /api/auth/login**
  - Descrição: Realiza login e retorna um token JWT.
  - Body: `{ "username": "string", "password": "string" }`
  - Resposta: `{ "access_token": "jwt-token" }`

- **POST /api/auth/logout**
  - Descrição: Invalida o token JWT atual.
  - Header: `Authorization: Bearer <token>`
  - Resposta: `204 No Content`

---

## 📊 Dashboard

- **GET /api/dashboard/summary**
  - Descrição: Retorna estatísticas resumidas do sistema.
  - Header: `Authorization: Bearer <token>`
  - Resposta: `{ "total_surebets": 123, "profit": 456.78, ... }`

- **GET /api/dashboard/opportunities**
  - Descrição: Lista oportunidades de arbitragem detectadas.
  - Parâmetros: `?sport=FOOTBALL&min_profit=2`
  - Resposta: `[{ "id": 1, "sport": "FOOTBALL", "profit": 2.5, ... }]`

---

## ⚙️ Administração

- **GET /api/admin/config**
  - Descrição: Retorna as configurações atuais do sistema.
  - Header: `Authorization: Bearer <token>`

- **POST /api/admin/config**
  - Descrição: Atualiza configurações do sistema.
  - Body: `{ "max_stake": 1000, ... }`

- **GET /api/admin/users**
  - Descrição: Lista usuários administradores.

---

## 🏦 Adaptadores de Bookmakers

- **GET /api/adapters/list**
  - Descrição: Lista adaptadores disponíveis e status.

- **POST /api/adapters/refresh**
  - Descrição: Força atualização dos dados dos bookmakers.

---

## 🩺 Health & Metrics

- **GET /health**
  - Descrição: Health check da aplicação.
  - Resposta: `{ "status": "ok" }`

- **GET /metrics**
  - Descrição: Métricas Prometheus para monitoramento.

---

## 🔒 Segurança

- Todos os endpoints protegidos exigem JWT no header `Authorization`.
- Limite de requisições por minuto (rate limiting).
- Todas as respostas seguem padrão JSON.

---

## Exemplos de Uso

```bash
curl -X POST http://localhost:5001/api/auth/login -d '{"username":"admin","password":"senha"}'
curl -H "Authorization: Bearer <token>" http://localhost:5001/api/dashboard/summary
```

---

Consulte a documentação OpenAPI/Swagger para detalhes completos de cada endpoint.
