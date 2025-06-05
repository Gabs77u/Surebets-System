# 🎯 Sistema de Surebets - Detecção de Arbitragem Esportiva

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()
[![Security](https://img.shields.io/badge/Security-OWASP%20Top%2010-red.svg)]()

> Sistema profissional para detecção e análise de oportunidades de arbitragem em apostas esportivas com arquitetura modular enterprise-ready, segurança avançada e validação rigorosa.

## 📋 Índice

- [Principais Alterações](#-principais-alterações-recentes)
- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Arquitetura](#-arquitetura)
- [Como Iniciar](#-como-iniciar-a-aplicação)
- [Configuração](#-configuração)
- [Testes](#-testes)
- [Deploy](#-deploy)
- [Documentação](#-documentação)
- [Contribuição](#-contribuição)
- [Status do Projeto](#-status-do-projeto)
- [Suporte](#-suporte)
- [Licença](#-licença)

---

## 🆕 Principais Alterações Recentes

### 🔒 Segurança e Autenticação (NOVA IMPLEMENTAÇÃO)
- **Sistema JWT Avançado**: 
  - Autenticação robusta com access e refresh tokens
  - Blacklist de tokens (Redis/memória) para logout seguro
  - Sistema granular de roles (admin/operator/viewer)
  - Suporte a cookies seguros para SPAs
  - Renovação automática transparente

- **Validação Rigorosa com Pydantic**:
  - Schemas de validação em todos os endpoints
  - Sanitização automática contra XSS
  - Detecção de SQL Injection
  - Validação de força de senha
  - Headers de segurança obrigatórios

- **Proteções Avançadas**:
  - Rate limiting configurável por IP
  - CSRF protection implementado
  - Logging estruturado de eventos de segurança
  - Monitoramento de tentativas de ataque

### 🧪 Sistema de Testes Expandido
- **Testes de Segurança**: 
  - `backend/tests/security/` com testes de penetração
  - Validação contra payloads maliciosos
  - Fuzzing automatizado
  - Testes de escalação de privilégios

- **Testes de Integração JWT**:
  - `backend/tests/integration/test_jwt_auth.py`
  - Fluxo completo de autenticação
  - Testes de roles e permissões
  - Validação de blacklist de tokens

- **Cobertura Ampliada**:
  - Testes unitários para auth e validação
  - Performance testing com cenários reais
  - Mocks inteligentes para APIs externas

### 🏗️ Arquitetura Modular Consolidada
- **Apps principais em `backend/apps/`** (dashboard, admin_api, adapters)
- **Utilitários centrais em `backend/core/`** (auth, i18n, validation)
- **Serviços de negócio em `backend/services/`**
- **Banco de dados em `backend/database/`** (SQLite configurável)
- **Configurações centralizadas em `config/settings.py`**
- **Docker e scripts de automação em `docker/`**

### 📚 Documentação Profissional Expandida
- **[JWT Frontend Integration Guide](JWT_FRONTEND_INTEGRACAO.md)**: Integração completa com React/Vue
- **[Security Guide](SECURITY.md)**: Documentação abrangente de segurança
- **[API Documentation](API.md)**: Endpoints atualizados com validação
- **[Architecture Guide](ARCHITECTURE.md)**: Arquitetura de segurança detalhada

### 🔧 Melhorias de Produção
- **Configuração por Ambiente**: Development vs Production
- **Health Checks Avançados**: `/health` com status detalhado
- **Métricas Prometheus**: `/metrics` para monitoramento
- **Backup Automatizado**: Configurações e dados
- **Deploy Seguro**: Containers hardened, usuário não-root

---

## 🎯 Visão Geral

O Sistema de Surebets é uma aplicação Python enterprise-ready que detecta automaticamente oportunidades de arbitragem em múltiplas casas de apostas esportivas. Completamente refatorado com **segurança avançada**, **validação rigorosa** e **arquitetura modular** seguindo padrões enterprise.

### 🌟 Principais Características

- **🔒 Segurança Enterprise**: JWT avançado, validação Pydantic, proteção OWASP Top 10
- **🔍 Detecção Automática**: Identifica oportunidades de arbitragem em tempo real
- **📊 Dashboard Interativo**: Interface web moderna com gráficos e estatísticas
- **🎭 Sistema de Roles**: Controle granular de acesso (admin/operator/viewer)
- **🌐 Multi-idioma**: Suporte para Português e Inglês
- **🏢 Arquitetura Enterprise**: Estrutura modular e profissional
- **🛡️ Proteções Avançadas**: Rate limiting, XSS, SQL injection, CSRF
- **📈 Monitoramento**: Logs profissionais e métricas de performance
- **🐳 Containerização**: Deploy com Docker e Docker Compose
- **⚡ Performance**: Cache Redis e otimizações de performance

## ✨ Funcionalidades

### 🎲 Core Features
- **Detecção de Arbitragem**: Algoritmos avançados para identificar oportunidades
- **Múltiplas Casas de Apostas**: Suporte extensível para diferentes bookmakers
- **Análise em Tempo Real**: Processamento contínuo de odds e oportunidades
- **Filtros Avançados**: Filtros personalizáveis por esporte, liga e mercado

### 🔒 Segurança e Autenticação
- **Sistema JWT Robusto**: Access/refresh tokens com blacklist
- **Roles Granulares**: Admin, operador, visualizador
- **Validação Rigorosa**: Pydantic schemas em todos os endpoints
- **Proteções Web**: XSS, SQL injection, CSRF, rate limiting
- **Audit Trail**: Logging de eventos de segurança

### 📊 Interface e Visualização
- **Dashboard Web**: Interface Flask moderna e responsiva
- **Gráficos Interativos**: Visualizações de dados com charts dinâmicos
- **Relatórios**: Exportação de dados e relatórios detalhados

### 🔧 Administração
- **Painel Admin**: Gerenciamento completo do sistema
- **Gestão de Usuários**: CRUD completo com validação
- **Configurações**: Ajustes flexíveis de parâmetros
- **Notificações**: Sistema de alertas e notificações
- **Logs**: Sistema de auditoria e troubleshooting

## 🏗️ Arquitetura

```
📦 Surebets-System/
├── 🚀 backend/              # Aplicação Backend
│   ├── 📱 apps/             # Aplicações Principais
│   │   ├── dashboard.py     # Dashboard Web Unificado
│   │   ├── admin_api.py     # API Administrativa Segura
│   │   └── adapters.py      # Adaptadores de Bookmakers
│   ├── 🔧 core/             # Utilities Centrais
│   │   ├── auth.py          # Sistema JWT Avançado
│   │   ├── validation.py    # Validação Pydantic
│   │   └── i18n.py         # Sistema de Internacionalização
│   ├── 🛠️ services/         # Serviços de Negócio
│   │   ├── arbitrage.py     # Engine de Arbitragem
│   │   └── notification.py  # Sistema de Notificações
│   ├── 🗄️ database/         # Componentes de Banco
│   └── 🧪 tests/            # Testes Estruturados
│       ├── unit/              # Testes unitários
│       ├── integration/       # Testes de integração JWT
│       ├── security/          # Testes de segurança
│       └── performance/       # Testes de performance
├── ⚙️ config/               # Configurações
│   └── settings.py         # Settings Centralizados
├── 🐳 docker/               # Container Setup
├── 📁 src/                  # Entry Point
│   ├── main.py             # Script Principal
│   └── requirements.txt    # Dependências Python
└── 📚 docs/                 # Documentação Expandida
    ├── JWT_FRONTEND_INTEGRACAO.md  # Novo: Guia JWT
    ├── SECURITY.md                 # Novo: Segurança
    ├── API.md                      # API atualizada
    ├── ARCHITECTURE.md             # Arquitetura
    ├── PRODUCTION_ROADMAP.md
    └── DESENVOLVIMENTO_COMPLETO.md
```

### 🔗 Padrões Arquiteturais

- **Separation of Concerns**: Módulos especializados e bem definidos
- **Dependency Injection**: Injeção de dependências para testabilidade
- **Factory Pattern**: Criação de adaptadores de bookmakers
- **Observer Pattern**: Sistema de notificações e eventos
- **Strategy Pattern**: Algoritmos de arbitragem intercambiáveis
- **Defense in Depth**: Múltiplas camadas de segurança

## 🚀 Como Iniciar a Aplicação

### 🐳 Execução Recomendada com Docker Compose

```bash
# Clone o repositório
git clone https://github.com/Gabs77u/Surebets-System.git
cd Surebets-System

# Suba todos os serviços (backend, frontend, banco, redis, etc)
docker-compose -f docker/docker-compose.yml up -d

# Para visualizar os logs em tempo real:
docker-compose -f docker/docker-compose.yml logs -f

# Para parar e remover os containers:
docker-compose -f docker/docker-compose.yml down

# Para reiniciar após alterações:
docker-compose -f docker/docker-compose.yml restart

# Para acessar o banco SQLite manualmente:
docker exec -it <nome_do_container_backend> sqlite3 /app/data/surebets.db

# Para rodar migrações ou scripts utilitários:
docker-compose -f docker/docker-compose.yml exec backend python backend/migrate_to_sqlite.py

# Dica: Para ambiente de produção, utilize o arquivo docker-compose.prod.yml 
# e configure as variáveis de ambiente de segurança adequadas.
```

### 🐍 Execução Local (Desenvolvimento)

```bash
# 1. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows

# 2. Instale as dependências
pip install -r src/requirements.txt

# 3. Configure as variáveis de ambiente de segurança
cp config/settings.example.py config/settings.py
# Edite config/settings.py conforme necessário

# 4. Execute o sistema principal
python src/main.py

# Ou execute módulos específicos
python -m backend.apps.dashboard
python -m backend.apps.admin_api
```

## 🔧 Configuração

### ⚙️ Variáveis de Ambiente Obrigatórias

```bash
# Configurações básicas
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///surebets.db

# JWT Security (OBRIGATÓRIO)
JWT_SECRET_KEY=your-256-bit-secret-key
JWT_ACCESS_TOKEN_EXPIRES_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRES_DAYS=30

# Redis (Cache e Blacklist de Tokens)
REDIS_URL=redis://localhost:6379/0

# Security Settings
ENVIRONMENT=production
RATE_LIMIT_PER_MINUTE=100
ENABLE_CORS=false

# APIs de Bookmakers
BOOKMAKER_API_KEY=your-api-key
RATE_LIMIT=100

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/surebets.log

# Admin Account (para bootstrap)
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=pbkdf2:sha256:150000$...
```

### 📊 Configurações do Sistema

```python
# config/settings.py
ARBITRAGE_SETTINGS = {
    'min_profit': 2.0,          # Lucro mínimo (%)
    'max_stake': 1000.0,        # Aposta máxima
    'check_interval': 30,       # Intervalo de verificação (s)
}

NOTIFICATION_SETTINGS = {
    'email_enabled': True,
    'sms_enabled': False,
    'webhook_url': 'https://your-webhook.com'
}

# Configurações de segurança por ambiente
SECURITY_SETTINGS = {
    'development': {
        'blacklist_backend': 'memory',
        'cors_origins': ['*'],
        'rate_limit': 1000,
    },
    'production': {
        'blacklist_backend': 'redis',
        'cors_origins': ['https://yourdomain.com'],
        'rate_limit': 100,
    }
}
```

## 🧪 Testes

### 🔍 Executar Testes

```bash
# Testes unitários
pytest backend/tests/unit/ -v

# Testes de integração (incluindo JWT)
pytest backend/tests/integration/ -v

# Testes de segurança
pytest backend/tests/security/ -v

# Testes de performance
pytest backend/tests/performance/ -v

# Testes completos com coverage
pytest --cov=backend backend/tests/ --cov-report=html

# Testes específicos de autenticação
pytest backend/tests/integration/test_jwt_auth.py -v

# Testes de penetração (simulação de ataques)
pytest backend/tests/security/test_penetration.py -v
```

### 📊 Coverage Report

```bash
# Gerar relatório de cobertura
coverage run -m pytest
coverage report
coverage html  # Relatório HTML em htmlcov/

# Coverage específico de segurança
coverage run -m pytest backend/tests/security/
coverage report --include="backend/core/auth.py,backend/core/validation.py"
```

### 🛡️ Testes de Segurança

```bash
# Análise estática de segurança
bandit -r backend/ -f json -o security-report.json

# Verificação de dependências vulneráveis
safety check
pip-audit

# Testes de carga para rate limiting
locust -f backend/tests/performance/locustfile.py
```

## 🚀 Deploy

### 🌍 Ambientes

- **Development**: `http://localhost:5000` (Blacklist em memória, CORS permissivo)
- **Staging**: `em breve` (Redis, logs detalhados)
- **Production**: `em breve` (Redis, logs estruturados, rate limiting agressivo)

### 🚀 Deploy para Produção

```bash
# Build e push da imagem com security hardening
docker build -t surebets-system:latest .
docker tag surebets-system:latest registry.com/surebets-system:latest
docker push registry.com/surebets-system:latest

# Deploy com Docker Compose (produção)
docker-compose -f docker/docker-compose.prod.yml up -d

# Verificar saúde do serviço
curl https://yourdomain.com/health
curl https://yourdomain.com/metrics

# Testar autenticação
curl -X POST https://yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}'
```

### 📈 Monitoramento

- **Health Checks**: `/health`, `/ready`
- **Metrics**: `/metrics` (Prometheus format)
- **Security Events**: Logs estruturados via ELK stack
- **JWT Monitoring**: Blacklist size, token refresh rate
- **Alertas**: PagerDuty/Slack integration para eventos de segurança

## 📖 Documentação

### 📚 Documentação Principal
- **[Documentação Completa](DESENVOLVIMENTO_COMPLETO.md)**
- **[Roadmap de Produção](PRODUCTION_ROADMAP.md)**
- **[Guia de Arquitetura](ARCHITECTURE.md)**
- **[Guia de Deployment](DEPLOYMENT.md)**

### 🔒 Documentação de Segurança (NOVA)
- **[Guia de Segurança](SECURITY.md)**: Segurança abrangente e OWASP Top 10
- **[API Documentation](API.md)**: Endpoints atualizados com validação
- **[JWT Frontend Integration](JWT_FRONTEND_INTEGRACAO.md)**: Integração React/Vue

### 👥 Documentação para Desenvolvedores
- **[Contributing Guidelines](CONTRIBUTING.md)**
- **[Performance Guide](PERFORMANCE.md)**
- **[Changelog](CHANGELOG.md)**

## 🤝 Contribuição

### 🛠️ Como Contribuir

1. **Fork** o projeto
2. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra** um Pull Request

### 📝 Padrões de Código

- **Python**: PEP 8, Black formatter
- **Security**: Todos os inputs devem ser validados com Pydantic
- **Authentication**: JWT obrigatório para endpoints sensíveis
- **Commits**: Conventional Commits
- **Tests**: Cobertura mínima de 90%, incluindo testes de segurança
- **Documentation**: Docstrings obrigatórias

### 🔍 Code Review

- Todos os PRs precisam de aprovação
- Testes automatizados devem passar (incluindo segurança)
- Cobertura de código mantida
- Análise de segurança com Bandit
- Documentação atualizada

## 📋 Status, Roadmap e Checklist

Toda a evolução do projeto, conquistas, status de produção e próximos passos estão centralizados em [CHECKLIST_PRODUCAO.md](CHECKLIST_PRODUCAO.md).

Consulte o checklist para:
- Status atual
- Roadmap detalhado
- Métricas e conquistas
- Próximos passos

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- **Flask Team**: Framework web fantástico
- **Pydantic Team**: Validação robusta e type safety
- **Flask-JWT-Extended**: Sistema JWT robusto
- **Python Community**: Ecosystem incrível de segurança
- **OWASP**: Guidelines de segurança web
- **Contributors**: Todos que contribuíram para este projeto
- **Security Researchers**: Feedback valioso para melhorias de segurança
- **Beta Testers**: Feedback valioso durante desenvolvimento

---

<div align="center">

**[⬆ Voltar ao Topo](#-sistema-de-surebets---detecção-de-arbitragem-esportiva)**

Feito com ❤️ e 🔒 pela equipe Surebets Hunters

[![Security](https://img.shields.io/badge/Security-First-red.svg)]() [![Tests](https://img.shields.io/badge/Tests-Passing-green.svg)]() [![Coverage](https://img.shields.io/badge/Coverage-90%25-brightgreen.svg)]()

</div>
