# 🛠️ Makefile - Sistema de Surebets
# Comandos para desenvolvimento, teste e deploy

# =============================================================================
# CONFIGURAÇÕES
# =============================================================================
.PHONY: help install dev test build clean docker-build docker-run docker-stop deploy

# Variáveis
PROJECT_NAME = surebets-system
DOCKER_IMAGE = $(PROJECT_NAME):latest
DOCKER_TAG = $(PROJECT_NAME):$(shell git rev-parse --short HEAD)
PYTHON = python3
PIP = pip3

# Cores para output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

# =============================================================================
# HELP
# =============================================================================
help: ## 📖 Mostra esta mensagem de ajuda
	@echo "$(BLUE)🎯 Sistema de Surebets - Comandos Disponíveis$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(GREEN)  %-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)📋 Exemplos de uso:$(NC)"
	@echo "  make install     # Instalar dependências"
	@echo "  make dev         # Executar em modo desenvolvimento"
	@echo "  make test        # Executar testes"
	@echo "  make build       # Build da aplicação"
	@echo "  make docker-up   # Executar com Docker Compose"

# =============================================================================
# INSTALAÇÃO E SETUP
# =============================================================================
install: ## 📦 Instala todas as dependências
	@echo "$(BLUE)📦 Instalando dependências...$(NC)"
	@$(PIP) install --upgrade pip
	@$(PIP) install -r src/requirements.txt
	@echo "$(GREEN)✅ Dependências instaladas com sucesso!$(NC)"

install-dev: ## 🛠️ Instala dependências de desenvolvimento
	@echo "$(BLUE)🛠️ Instalando dependências de desenvolvimento...$(NC)"
	@$(PIP) install --upgrade pip
	@$(PIP) install -r src/requirements.txt
	@$(PIP) install pytest pytest-cov black flake8 mypy pre-commit
	@echo "$(GREEN)✅ Dependências de desenvolvimento instaladas!$(NC)"

setup: ## ⚙️ Configuração inicial do projeto
	@echo "$(BLUE)⚙️ Configurando projeto...$(NC)"
	@mkdir -p logs data static temp
	@cp config/settings.example.py config/settings.py 2>/dev/null || true
	@echo "$(GREEN)✅ Projeto configurado!$(NC)"

# =============================================================================
# DESENVOLVIMENTO
# =============================================================================
dev: ## 🚀 Executa aplicação em modo desenvolvimento
	@echo "$(BLUE)🚀 Iniciando aplicação em modo desenvolvimento...$(NC)"
	@export FLASK_ENV=development && $(PYTHON) src/main.py

dev-dashboard: ## 📊 Executa apenas o dashboard
	@echo "$(BLUE)📊 Iniciando dashboard...$(NC)"
	@export FLASK_ENV=development && $(PYTHON) -m backend.apps.dashboard

dev-admin: ## 🔐 Executa apenas a API administrativa
	@echo "$(BLUE)🔐 Iniciando API administrativa...$(NC)"
	@export FLASK_ENV=development && $(PYTHON) -m backend.apps.admin_api

# =============================================================================
# QUALIDADE DE CÓDIGO
# =============================================================================
lint: ## 🔍 Verifica qualidade do código
	@echo "$(BLUE)🔍 Verificando qualidade do código...$(NC)"
	@flake8 backend/ frontend/ src/ --max-line-length=88 --extend-ignore=E203,W503
	@black --check backend/ frontend/ src/
	@echo "$(GREEN)✅ Código em conformidade!$(NC)"

format: ## 🎨 Formata o código
	@echo "$(BLUE)🎨 Formatando código...$(NC)"
	@black backend/ frontend/ src/
	@echo "$(GREEN)✅ Código formatado!$(NC)"

type-check: ## 🔬 Verifica tipos com mypy
	@echo "$(BLUE)🔬 Verificando tipos...$(NC)"
	@mypy backend/ frontend/ src/ --ignore-missing-imports
	@echo "$(GREEN)✅ Tipos verificados!$(NC)"

# =============================================================================
# TESTES
# =============================================================================
test: ## 🧪 Executa todos os testes
	@echo "$(BLUE)🧪 Executando testes...$(NC)"
	@$(PYTHON) -m pytest tests/ -v
	@echo "$(GREEN)✅ Testes concluídos!$(NC)"

test-unit: ## 🔬 Executa testes unitários
	@echo "$(BLUE)🔬 Executando testes unitários...$(NC)"
	@$(PYTHON) -m pytest tests/unit/ -v

test-integration: ## 🔗 Executa testes de integração
	@echo "$(BLUE)🔗 Executando testes de integração...$(NC)"
	@$(PYTHON) -m pytest tests/integration/ -v

test-coverage: ## 📊 Executa testes com coverage
	@echo "$(BLUE)📊 Executando testes com coverage...$(NC)"
	@$(PYTHON) -m pytest tests/ --cov=backend --cov=frontend --cov-report=html --cov-report=term
	@echo "$(GREEN)✅ Relatório de coverage gerado em htmlcov/$(NC)"

# =============================================================================
# BUILD E EMPACOTAMENTO
# =============================================================================
build: ## 📦 Build da aplicação
	@echo "$(BLUE)📦 Fazendo build da aplicação...$(NC)"
	@$(PYTHON) setup.py build
	@echo "$(GREEN)✅ Build concluído!$(NC)"

clean: ## 🧹 Limpa arquivos temporários
	@echo "$(BLUE)🧹 Limpando arquivos temporários...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/
	@echo "$(GREEN)✅ Limpeza concluída!$(NC)"

# =============================================================================
# DOCKER
# =============================================================================
docker-build: ## 🐳 Build da imagem Docker
	@echo "$(BLUE)🐳 Fazendo build da imagem Docker...$(NC)"
	@docker build -t $(DOCKER_IMAGE) -t $(DOCKER_TAG) .
	@echo "$(GREEN)✅ Imagem Docker criada: $(DOCKER_IMAGE)$(NC)"

docker-run: ## 🏃 Executa container Docker
	@echo "$(BLUE)🏃 Executando container Docker...$(NC)"
	@docker run -d --name $(PROJECT_NAME) -p 5000:5000 -p 5001:5001 $(DOCKER_IMAGE)
	@echo "$(GREEN)✅ Container executando em http://localhost:5000$(NC)"

docker-stop: ## ⏹️ Para container Docker
	@echo "$(BLUE)⏹️ Parando container Docker...$(NC)"
	@docker stop $(PROJECT_NAME) 2>/dev/null || true
	@docker rm $(PROJECT_NAME) 2>/dev/null || true
	@echo "$(GREEN)✅ Container parado!$(NC)"

docker-up: ## 🚀 Executa stack completa com Docker Compose
	@echo "$(BLUE)🚀 Iniciando stack completa...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)✅ Stack iniciada!$(NC)"
	@echo "$(YELLOW)📋 Serviços disponíveis:$(NC)"
	@echo "  • Dashboard: http://localhost:5000"
	@echo "  • Admin API: http://localhost:5001"
	@echo "  • Grafana: http://localhost:3000"
	@echo "  • Prometheus: http://localhost:9090"
	@echo "  • Portainer: http://localhost:9000"

docker-down: ## ⬇️ Para stack Docker Compose
	@echo "$(BLUE)⬇️ Parando stack...$(NC)"
	@docker-compose down
	@echo "$(GREEN)✅ Stack parada!$(NC)"

docker-logs: ## 📝 Mostra logs dos containers
	@echo "$(BLUE)📝 Logs dos containers:$(NC)"
	@docker-compose logs -f

# =============================================================================
# BANCO DE DADOS
# =============================================================================
db-migrate: ## 🗄️ Executa migrações do banco
	@echo "$(BLUE)🗄️ Executando migrações...$(NC)"
	@$(PYTHON) -c "from backend.database import migrate; migrate()"
	@echo "$(GREEN)✅ Migrações executadas!$(NC)"

db-seed: ## 🌱 Popula banco com dados de exemplo
	@echo "$(BLUE)🌱 Populando banco com dados de exemplo...$(NC)"
	@$(PYTHON) -c "from backend.database import seed; seed()"
	@echo "$(GREEN)✅ Dados de exemplo inseridos!$(NC)"

db-reset: ## 🔄 Reseta o banco de dados
	@echo "$(BLUE)🔄 Resetando banco de dados...$(NC)"
	@rm -f *.db *.sqlite *.sqlite3
	@make db-migrate
	@make db-seed
	@echo "$(GREEN)✅ Banco resetado!$(NC)"

# =============================================================================
# MONITORAMENTO E LOGS
# =============================================================================
logs: ## 📝 Mostra logs da aplicação
	@echo "$(BLUE)📝 Logs da aplicação:$(NC)"
	@tail -f logs/surebets.log 2>/dev/null || echo "$(YELLOW)⚠️ Arquivo de log não encontrado$(NC)"

logs-error: ## ❌ Mostra logs de erro
	@echo "$(BLUE)❌ Logs de erro:$(NC)"
	@tail -f logs/error.log 2>/dev/null || echo "$(YELLOW)⚠️ Arquivo de log de erro não encontrado$(NC)"

health: ## ❤️ Verifica saúde da aplicação
	@echo "$(BLUE)❤️ Verificando saúde da aplicação...$(NC)"
	@curl -f http://localhost:5000/health 2>/dev/null && echo "$(GREEN)✅ Aplicação saudável!$(NC)" || echo "$(RED)❌ Aplicação não responde$(NC)"

# =============================================================================
# DEPLOY E PRODUÇÃO
# =============================================================================
deploy-staging: ## 🚀 Deploy para staging
	@echo "$(BLUE)🚀 Fazendo deploy para staging...$(NC)"
	@docker-compose -f docker/docker-compose.staging.yml up -d
	@echo "$(GREEN)✅ Deploy para staging concluído!$(NC)"

deploy-prod: ## 🏭 Deploy para produção
	@echo "$(BLUE)🏭 Fazendo deploy para produção...$(NC)"
	@docker-compose -f docker/docker-compose.prod.yml up -d
	@echo "$(GREEN)✅ Deploy para produção concluído!$(NC)"

backup: ## 💾 Faz backup dos dados
	@echo "$(BLUE)💾 Fazendo backup...$(NC)"
	@mkdir -p backups/$(shell date +%Y%m%d_%H%M%S)
	@cp -r data/ backups/$(shell date +%Y%m%d_%H%M%S)/
	@echo "$(GREEN)✅ Backup concluído!$(NC)"

# =============================================================================
# SEGURANÇA
# =============================================================================
security-check: ## 🔒 Verifica vulnerabilidades de segurança
	@echo "$(BLUE)🔒 Verificando vulnerabilidades...$(NC)"
	@pip-audit --desc
	@echo "$(GREEN)✅ Verificação de segurança concluída!$(NC)"

# =============================================================================
# UTILITÁRIOS
# =============================================================================
requirements: ## 📋 Atualiza arquivo de requisitos
	@echo "$(BLUE)📋 Atualizando requirements.txt...$(NC)"
	@pip freeze > src/requirements.txt
	@echo "$(GREEN)✅ Requirements atualizados!$(NC)"

version: ## 📊 Mostra versão da aplicação
	@echo "$(BLUE)📊 Versão da aplicação:$(NC)"
	@$(PYTHON) -c "from src.version import __version__; print(__version__)" 2>/dev/null || echo "2.0.0"

info: ## ℹ️ Mostra informações do sistema
	@echo "$(BLUE)ℹ️ Informações do sistema:$(NC)"
	@echo "Python: $(shell python --version)"
	@echo "Pip: $(shell pip --version)"
	@echo "Docker: $(shell docker --version 2>/dev/null || echo 'Não instalado')"
	@echo "Docker Compose: $(shell docker-compose --version 2>/dev/null || echo 'Não instalado')"

# =============================================================================
# TARGETS ESPECIAIS
# =============================================================================
.DEFAULT_GOAL := help

# Verificar se está em ambiente virtual
check-venv:
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "$(YELLOW)⚠️ Aviso: Não está em um ambiente virtual!$(NC)"; \
	fi

# Target que roda antes de comandos que precisam de ambiente
pre-run: check-venv
