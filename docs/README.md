# 🎯 Sistema de Surebets - Detecção de Arbitragem Esportiva

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

> Sistema profissional para detecção e análise de oportunidades de arbitragem em apostas esportivas com arquitetura modular enterprise-ready.

## 📋 Índice

- [🎯 Visão Geral](#-visão-geral)
- [✨ Funcionalidades](#-funcionalidades)
- [🏗️ Arquitetura](#-arquitetura)
- [🚀 Quick Start](#-quick-start)
- [🛠️ Instalação](#-instalação)
- [📖 Documentação](#-documentação)
- [🔧 Configuração](#-configuração)
- [🧪 Testes](#-testes)
- [🚀 Deploy](#-deploy)
- [🤝 Contribuição](#-contribuição)

## 🎯 Visão Geral

O Sistema de Surebets é uma aplicação Python profissional que detecta automaticamente oportunidades de arbitragem em múltiplas casas de apostas esportivas. O sistema foi completamente refatorado seguindo padrões enterprise com arquitetura modular, separação de responsabilidades e preparação para produção.

### 🌟 Principais Características

- **🔍 Detecção Automática**: Identifica oportunidades de arbitragem em tempo real
- **📊 Dashboard Interativo**: Interface web moderna com gráficos e estatísticas
- **🌐 Multi-idioma**: Suporte para Português e Inglês
- **🏢 Arquitetura Enterprise**: Estrutura modular e profissional
- **🔒 Segurança**: Autenticação, rate limiting e proteções integradas
- **📈 Monitoramento**: Logs profissionais e métricas de performance
- **🐳 Containerização**: Deploy com Docker e Docker Compose
- **⚡ Performance**: Cache Redis e otimizações de performance

## ✨ Funcionalidades

### 🎲 Core Features
- **Detecção de Arbitragem**: Algoritmos avançados para identificar oportunidades
- **Múltiplas Casas de Apostas**: Suporte extensível para diferentes bookmakers
- **Análise em Tempo Real**: Processamento contínuo de odds e oportunidades
- **Filtros Avançados**: Filtros personalizáveis por esporte, liga e mercado

### 📊 Interface e Visualização
- **Dashboard Web**: Interface Flask moderna e responsiva
- **Interface Desktop**: Aplicação Tkinter nativa
- **Gráficos Interativos**: Visualizações de dados com charts dinâmicos
- **Relatórios**: Exportação de dados e relatórios detalhados

### 🔧 Administração
- **Painel Admin**: Gerenciamento completo do sistema
- **Configurações**: Ajustes flexíveis de parâmetros
- **Notificações**: Sistema de alertas e notificações
- **Logs**: Sistema de auditoria e troubleshooting

## 🏗️ Arquitetura

```
📦 Surebets-System/
├── 🚀 backend/              # Aplicação Backend
│   ├── 📱 apps/             # Aplicações Principais
│   │   ├── dashboard.py     # Dashboard Web Unificado
│   │   ├── admin_api.py     # API Administrativa
│   │   └── adapters.py      # Adaptadores de Bookmakers
│   ├── 🔧 core/             # Utilities Centrais
│   │   └── i18n.py         # Sistema de Internacionalização
│   ├── 🛠️ services/         # Serviços de Negócio
│   │   ├── arbitrage.py     # Engine de Arbitragem
│   │   └── notification.py  # Sistema de Notificações
│   └── 🗄️ database/         # Componentes de Banco
├── 🖥️ frontend/             # Interfaces de Usuário
│   └── tinker_ui.py        # Interface Tkinter
├── ⚙️ config/               # Configurações
│   └── settings.py         # Settings Centralizados
├── 🐳 docker/               # Container Setup
├── 📁 src/                  # Entry Point
│   ├── main.py             # Script Principal
│   └── requirements.txt    # Dependências Python
└── 📚 docs/                 # Documentação
    ├── PRODUCTION_ROADMAP.md
    └── DESENVOLVIMENTO_COMPLETO.md
```

### 🔗 Padrões Arquiteturais

- **Separation of Concerns**: Módulos especializados e bem definidos
- **Dependency Injection**: Injeção de dependências para testabilidade
- **Factory Pattern**: Criação de adaptadores de bookmakers
- **Observer Pattern**: Sistema de notificações e eventos
- **Strategy Pattern**: Algoritmos de arbitragem intercambiáveis

## 🚀 Quick Start

### ⚡ Execução Rápida com Docker

```bash
# Clone o repositório
git clone https://github.com/Gabs77u/Surebets-System.git
cd surebets-system

# Execute com Docker Compose
docker-compose up -d

# Acesse a aplicação
# Dashboard: http://localhost:5000
# Admin API: http://localhost:5001
```

### 🐍 Execução Local

```bash
# Instale as dependências
pip install -r src/requirements.txt

# Execute o sistema
python src/main.py

# Ou execute módulos específicos
python -m backend.apps.dashboard
python -m backend.apps.admin_api
```

## 🛠️ Instalação

### 📋 Pré-requisitos

- **Python**: 3.9 ou superior
- **Docker**: 20.0+ (opcional, recomendado)
- **Redis**: 6.0+ (para cache em produção)
- **PostgreSQL**: 13+ (para produção)

### 🔧 Instalação Local

1. **Clone o Repositório**
   ```bash
   git clone https://github.com/Gabs77u/Surebets-System.git
   cd surebets-system
   ```

2. **Ambiente Virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. **Instalar Dependências**
   ```bash
   pip install -r src/requirements.txt
   ```

4. **Configurar Ambiente**
   ```bash
   cp config/settings.example.py config/settings.py
   # Edite config/settings.py conforme necessário
   ```

5. **Executar**
   ```bash
   python src/main.py
   ```

### 🐳 Instalação com Docker

1. **Docker Compose (Recomendado)**
   ```bash
   docker-compose -f docker/docker-compose.yml up -d
   ```

2. **Docker Manual**
   ```bash
   # Build da imagem
   docker build -t surebets-system .
   
   # Execute o container
   docker run -p 5000:5000 -p 5001:5001 surebets-system
   ```

## 📖 Documentação

### 📚 Documentos Principais

- **[Documentação Completa](DESENVOLVIMENTO_COMPLETO.md)**: Guia completo de desenvolvimento
- **[Roadmap de Produção](PRODUCTION_ROADMAP.md)**: Plano detalhado para produção
- **[API Documentation](docs/API.md)**: Especificação das APIs
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Guia de deploy

### 🎓 Guias Específicos

- **[Architecture Guide](docs/ARCHITECTURE.md)**: Detalhes da arquitetura
- **[Contributing Guidelines](docs/CONTRIBUTING.md)**: Como contribuir
- **[Security Guide](docs/SECURITY.md)**: Práticas de segurança
- **[Performance Guide](docs/PERFORMANCE.md)**: Otimizações de performance

## 🔧 Configuração

### ⚙️ Variáveis de Ambiente

```bash
# Configurações básicas
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///surebets.db

# Redis (Cache)
REDIS_URL=redis://localhost:6379/0

# APIs de Bookmakers
BOOKMAKER_API_KEY=your-api-key
RATE_LIMIT=100

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/surebets.log
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
```

## 🧪 Testes

### 🔍 Executar Testes

```bash
# Testes unitários
pytest tests/unit/

# Testes de integração
pytest tests/integration/

# Testes completos com coverage
pytest --cov=backend tests/ --cov-report=html

# Testes de performance
locust -f tests/performance/locustfile.py
```

### 📊 Coverage Report

```bash
# Gerar relatório de cobertura
coverage run -m pytest
coverage report
coverage html  # Relatório HTML em htmlcov/
```

## 🚀 Deploy

### 🌍 Ambientes

- **Development**: `http://localhost:5000`
- **Staging**: `https://staging.surebets.com`
- **Production**: `https://surebets.com`

### 🚀 Deploy para Produção

```bash
# Build e push da imagem
docker build -t surebets-system:latest .
docker tag surebets-system:latest registry.com/surebets-system:latest
docker push registry.com/surebets-system:latest

# Deploy com Docker Compose
docker-compose -f docker/docker-compose.prod.yml up -d

# Verificar saúde do serviço
curl http://localhost:5000/health
```

### 📈 Monitoramento

- **Health Checks**: `/health`, `/ready`
- **Metrics**: `/metrics` (Prometheus format)
- **Logs**: Centralizados via ELK stack
- **Alertas**: PagerDuty/Slack integration

## 🤝 Contribuição

### 🛠️ Como Contribuir

1. **Fork** o projeto
2. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra** um Pull Request

### 📝 Padrões de Código

- **Python**: PEP 8, Black formatter
- **Commits**: Conventional Commits
- **Tests**: Cobertura mínima de 90%
- **Documentation**: Docstrings obrigatórias

### 🔍 Code Review

- Todos os PRs precisam de aprovação
- Testes automatizados devem passar
- Cobertura de código mantida
- Documentação atualizada

## 📊 Status do Projeto

### ✅ Funcionalidades Implementadas

- [x] **Arquitetura Unificada**: Sistema modular e profissional
- [x] **Dashboard Web**: Interface completa com Flask
- [x] **API Administrativa**: Endpoints de gerenciamento
- [x] **Sistema de Adaptadores**: Suporte a múltiplas casas de apostas
- [x] **Internacionalização**: Suporte PT-BR e EN
- [x] **Interface Desktop**: Aplicação Tkinter

### 🚧 Em Desenvolvimento

- [ ] **Autenticação JWT**: Sistema de autenticação robusto
- [ ] **Cache Redis**: Layer de cache para performance
- [ ] **Monitoring**: Métricas e alertas profissionais
- [ ] **CI/CD Pipeline**: Deploy automatizado
- [ ] **Testes Automatizados**: Suite completa de testes

### 🎯 Roadmap

1. **Q1 2025**: Implementação de segurança e autenticação
2. **Q2 2025**: Sistema de monitoring e observabilidade
3. **Q3 2025**: Otimizações de performance e cache
4. **Q4 2025**: Deploy automatizado e CI/CD

## 📞 Suporte

### 🆘 Precisa de Ajuda?

- **Issues**: [GitHub Issues](https://github.com/Gabs77u/surebets-system/issues)
- **Discussions**: [GitHub Discussions](https://github.com//surebets-system/discussions)
- **Email**: gabrielaraujoseven@gmail.com
- 

### 📚 Recursos Adicionais

- **NothingHere**

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- **Flask Team**: Framework web fantástico
- **Python Community**: Ecosystem incrível
- **Contributors**: Todos que contribuíram para este projeto
- **Beta Testers**: Feedback valioso durante desenvolvimento

---

<div align="center">

**[⬆ Voltar ao Topo](#-sistema-de-surebets---detecção-de-arbitragem-esportiva)**

Feito com ❤️ pela equipe Surebets Hunters

</div>
