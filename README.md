[![Docker](https://img.shields.io/badge/docker-ready-blue?logo=docker)](https://www.docker.com/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/)

# Surebets System

> 🇧🇷 Este projeto está disponível em português e inglês. <br>
> 🇺🇸 This project is available in Portuguese and English.

---

## 🇧🇷 Visão Geral

Sistema completo e automatizado para detecção de arbitragem esportiva (surebets), com backend robusto (Dash, Flask, FastAPI, PostgreSQL, notificações, adapters para múltiplas casas de apostas, painel admin) e frontend integrado. Pronto para deploy via Docker ou executável standalone.

## 🇺🇸 Overview

A complete and automated system for sports arbitrage (surebets) detection, with a robust backend (Dash, Flask, FastAPI, PostgreSQL, notifications, adapters for multiple bookmakers, admin panel) and integrated frontend. Ready for deployment via Docker or standalone executable.

---

## 🇧🇷 Funcionalidades Principais

- **Dashboard Web Moderno (Dash):** Visualização em tempo real das oportunidades de arbitragem.
- **Painel de Administração:** Configurações, notificações, overview do banco de dados e inserção de apostas com automações inteligentes.
- **Algoritmo de Detecção de Surebets:** Modular, eficiente e testado.
- **Banco de Dados PostgreSQL:** Schema otimizado, integração real, sugestões baseadas em histórico.
- **Sistema de Notificações:** WebSocket, Telegram, WhatsApp (configurável via variáveis de ambiente).
- **Adapters para Bookmakers:** Integração com Bet365, Pinnacle, Betfair, Super Odds (padrão Adapter, fácil expansão).
- **Internacionalização:** README, badges, changelog, licença MIT.
- **Automação Avançada:** Sugestões inteligentes, validação, autocomplete e limpeza automática no formulário de apostas.
- **Scripts de Build:** build.sh, build.bat, build.spec para PyInstaller, Dockerfile e docker-compose.yml.
- **Testes Unitários:** Para configurações, segurança e cache.

## 🇺🇸 Main Features

- **Modern Web Dashboard (Dash):** Real-time visualization of arbitrage opportunities.
- **Admin Panel:** Settings, notifications, database overview, and bet insertion with smart automations.
- **Surebets Detection Algorithm:** Modular, efficient, and tested.
- **PostgreSQL Database:** Optimized schema, real integration, history-based suggestions.
- **Notification System:** WebSocket, Telegram, WhatsApp (configurable via environment variables).
- **Bookmaker Adapters:** Integration with Bet365, Pinnacle, Betfair, Super Odds (Adapter pattern, easy expansion).
- **Internationalization:** README, badges, changelog, MIT license.
- **Advanced Automation:** Smart suggestions, validation, autocomplete, and automatic form cleaning.
- **Build Scripts:** build.sh, build.bat, build.spec for PyInstaller, Dockerfile, and docker-compose.yml.
- **Unit Tests:** For settings, security, and cache.

---

## 🇧🇷 Como Executar o Programa

### 1. Pré-requisitos
- Docker e Docker Compose **OU** Python 3.11+ instalado
- (Opcional) PostgreSQL local, se não usar Docker

### 2. Executando com Docker (Recomendado)

```bash
# No diretório raiz do projeto
bash docker-compose.yml up --build
```

- Acesse o painel Dash: [http://localhost:8050](http://localhost:8050)
- Acesse o painel Admin: [http://localhost:5000](http://localhost:5000)

O banco PostgreSQL será criado automaticamente (usuário: postgres, senha: postgres, banco: surebets).

### 3. Executando Manualmente (Windows/Linux)

```bash
# Instale as dependências
pip install -r requirements.txt

# (Opcional) Suba o PostgreSQL localmente e ajuste a variável POSTGRES_URL em config/settings.py

# Inicialize o banco (executado automaticamente pelo main.py)

# Execute o sistema
python main.py
```

- Painel Dash: http://localhost:8050
- Painel Admin: http://localhost:5000

### 4. Gerando Executável Standalone (PyInstaller)

```bash
bash build.sh
# ou no Windows
build.bat
```
O executável será gerado na sua Área de Trabalho.

---

## 🇺🇸 How to Run the Program

### 1. Prerequisites
- Docker and Docker Compose **OR** Python 3.11+ installed
- (Optional) Local PostgreSQL if not using Docker

### 2. Running with Docker (Recommended)

```bash
# In the project root directory
bash docker-compose.yml up --build
```

- Access Dash panel: [http://localhost:8050](http://localhost:8050)
- Access Admin panel: [http://localhost:5000](http://localhost:5000)

PostgreSQL will be created automatically (user: postgres, password: postgres, db: surebets).

### 3. Running Manually (Windows/Linux)

```bash
# Install dependencies
pip install -r requirements.txt

# (Optional) Start PostgreSQL locally and set POSTGRES_URL in config/settings.py

# Initialize the database (done automatically by main.py)

# Run the system
python main.py
```

- Dash panel: http://localhost:8050
- Admin panel: http://localhost:5000

### 4. Generating Standalone Executable (PyInstaller)

```bash
bash build.sh
# or on Windows
build.bat
```
The executable will be generated on your Desktop.

---

## 🇧🇷 Estrutura do Projeto

```
Surebets-System/
├── backend/
│   ├── app.py                # Painel Dash (frontend)
│   ├── admin_api.py          # API de administração (Flask)
│   ├── api_integrations/     # Adapters para casas de apostas
│   ├── arbitrage_calculator/ # Algoritmo de detecção de surebets
│   ├── bookmakers/           # Modelos de casas de apostas
│   ├── database/             # Banco de dados e schema
│   ├── notification_system/  # Notificações (WebSocket, Telegram, WhatsApp)
│   └── ...
├── config/                   # Configurações e segurança
├── frontend/                 # (Opcional) arquivos estáticos/templates
├── tests/                    # Testes unitários
├── main.py                   # Ponto de entrada unificado
├── requirements.txt          # Dependências Python
├── Dockerfile                # Build Docker
├── docker-compose.yml        # Orquestração Docker
├── README.md                 # Este arquivo
├── CHANGELOG.md              # Histórico de mudanças
└── LICENSE                   # Licença MIT
```

## 🇺🇸 Project Structure

```
Surebets-System/
├── backend/
│   ├── app.py                # Dash panel (frontend)
│   ├── admin_api.py          # Admin API (Flask)
│   ├── api_integrations/     # Bookmaker adapters
│   ├── arbitrage_calculator/ # Surebets detection algorithm
│   ├── bookmakers/           # Bookmaker models
│   ├── database/             # Database and schema
│   ├── notification_system/  # Notifications (WebSocket, Telegram, WhatsApp)
│   └── ...
├── config/                   # Settings and security
├── frontend/                 # (Optional) static/templates
├── tests/                    # Unit tests
├── main.py                   # Unified entry point
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker build
├── docker-compose.yml        # Docker orchestration
├── README.md                 # This file
├── CHANGELOG.md              # Changelog
└── LICENSE                   # MIT License
```

---

## 🇧🇷 Variáveis de Ambiente Importantes

- `POSTGRES_URL` (ex: postgresql://postgres:postgres@db:5432/surebets)
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- `WHATSAPP_API_URL`, `WHATSAPP_TOKEN`, `WHATSAPP_PHONE`
- `SECRET_KEY`

Essas variáveis podem ser definidas no ambiente ou diretamente em `config/settings.py`.

## 🇺🇸 Important Environment Variables

- `POSTGRES_URL` (e.g.: postgresql://postgres:postgres@db:5432/surebets)
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- `WHATSAPP_API_URL`, `WHATSAPP_TOKEN`, `WHATSAPP_PHONE`
- `SECRET_KEY`

These variables can be set in your environment or directly in `config/settings.py`.

---

## 🇧🇷 Testes

Execute os testes unitários com:
```bash
pytest tests/
```

## 🇺🇸 Tests

Run unit tests with:
```bash
pytest tests/
```

---

## 🇧🇷 Funcionalidades Faltantes / Melhorias Futuras

- **Autenticação/Admin Security:** Adicionar autenticação e controle de acesso ao painel admin.
- **Sugestões Inteligentes Avançadas:** Expandir autocomplete para mercados/bookmakers, histórico mais detalhado.
- **Melhorias no Frontend:** Internacionalização do painel, tratamento avançado de arquivos estáticos.
- **Cobertura de Testes:** Testes de integração e cobertura total.
- **Refatoração:** Remover código legado não utilizado e otimizar módulos.
- **Documentação Técnica:** Expandir documentação de APIs e exemplos de uso.

## 🇺🇸 Missing Features / Future Improvements

- **Authentication/Admin Security:** Add authentication and access control to the admin panel.
- **Advanced Smart Suggestions:** Expand autocomplete for markets/bookmakers, more detailed history.
- **Frontend Improvements:** Panel internationalization, advanced static file handling.
- **Test Coverage:** Integration tests and full coverage.
- **Refactoring:** Remove unused legacy code and optimize modules.
- **Technical Documentation:** Expand API documentation and usage examples.

---

## 🇧🇷 Licença

MIT License. Veja o arquivo [LICENSE](LICENSE).

## 🇺🇸 License

MIT License. See the [LICENSE](LICENSE) file.

---

## 🇧🇷 Contato

Dúvidas, sugestões ou bugs? Abra uma issue ou envie um e-mail para gabrielaraujo.dev@gmail.com

## 🇺🇸 Contact

Questions, suggestions or bugs? Open an issue or email gabrielaraujo.dev@gmail.com
