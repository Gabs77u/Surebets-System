import os
import logging
from dotenv import load_dotenv
from config.config_loader import CONFIG

# Carrega variáveis do .env.production automaticamente em produção
if os.getenv("FLASK_ENV") == "production":
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env.production")
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)

# Configurações gerais do sistema
APP_NAME = CONFIG["project"]["name"]
DEBUG = CONFIG["project"]["debug"]
PORT = CONFIG["server"]["port"]

# Configuração para módulos unificados
USE_UNIFIED_MODULES = True  # Não presente no YAML, manter padrão
UNIFIED_DASHBOARD_PORT = 8050  # Não presente no YAML, manter padrão
UNIFIED_ADMIN_API_PORT = 5000  # Não presente no YAML, manter padrão

# Configurações de integração
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE", "")

# Configuração de cache
CACHE_TIMEOUT = 60  # Não presente no YAML, manter padrão

# Configuração de banco de dados PostgreSQL
DATABASE_URL = os.getenv("POSTGRES_DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = f"postgresql://{CONFIG['postgres']['user']}:{CONFIG['postgres']['password']}@{CONFIG['postgres']['host']}:{CONFIG['postgres']['port']}/{CONFIG['postgres']['dbname']}"
DATABASE_BACKUP_DIR = None  # Não presente no YAML

# Configuração de banco de dados PostgreSQL para testes
if os.getenv("PYTEST_CURRENT_TEST"):
    # Força uso de banco de testes se rodando pytest
    DATABASE_URL = os.getenv("POSTGRES_DATABASE_URL_TEST") or os.getenv("DATABASE_URL_TEST")
    if not DATABASE_URL:
        # Banco padrão de testes
        DATABASE_URL = "postgresql://postgres:admin@localhost:5432/surebets_test"

# Configurações de pool de conexões
MAX_CONNECTIONS = CONFIG["postgres"]["pool_size"]
CONNECTION_TIMEOUT = 30.0  # Não presente no YAML

# Segurança
SECRET_KEY = CONFIG["security"]["secret_key"]
JWT_SECRET_KEY = CONFIG["security"]["secret_key"]
if not SECRET_KEY and not DEBUG:
    logging.warning(
        "AVISO: SECRET_KEY não definida, usando valor padrão para DEBUG. NÃO USE EM PRODUÇÃO."
    )
    SECRET_KEY = "debug-secret-key-do-not-use-in-prod"

ALLOWED_HOSTS = CONFIG["security"]["allowed_hosts"]
if not ALLOWED_HOSTS and not DEBUG:
    logging.warning(
        "AVISO: ALLOWED_HOSTS não definido, usando '*' para testes locais. NÃO USE EM PRODUÇÃO."
    )
    ALLOWED_HOSTS = "*"

ADMIN_API_URL = os.getenv("ADMIN_API_URL", "http://localhost:5000")
ADMIN_PASSWORD_HASH = os.getenv(
    "ADMIN_PASSWORD_HASH",
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
)

# Bookmakers
MOCK_BOOKMAKER_DATA = os.getenv("MOCK_BOOKMAKER_DATA", "false").lower() == "true"
BOOKMAKER_TIMEOUT = 20  # Não presente no YAML
BOOKMAKER_MAX_RETRIES = CONFIG["services"]["arbitrage"]["max_parallel_tasks"]
BOOKMAKER_RATE_LIMIT = 1.0  # Não presente no YAML
GLOBAL_MIN_ODDS = CONFIG["services"]["arbitrage"]["min_profit_percent"]
GLOBAL_MAX_ODDS = 1000  # Não presente no YAML

# APIs específicas
BET365_API_KEY = os.getenv("BET365_API_KEY")
PINNACLE_API_KEY = os.getenv("PINNACLE_API_KEY")
BETFAIR_API_KEY = os.getenv("BETFAIR_API_KEY")
SUPERODDS_API_KEY = os.getenv("SUPERODDS_API_KEY")

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Logging
LOG_LEVEL = CONFIG["logging"]["level"]
LOG_FILE = CONFIG["logging"]["file"]

# Rate Limiting
RATE_LIMIT = CONFIG["security"]["rate_limit_per_minute"]

# CORS
CORS_ORIGINS = CONFIG["server"]["cors_origins"]

# Dashboard UI
UI_THEME = CONFIG["ui"]["theme"]
UI_LANGUAGE = CONFIG["ui"]["language"]
UI_ITEMS_PER_PAGE = CONFIG["ui"]["items_per_page"]

# Parâmetros customizáveis
MAX_BET_VALUE = CONFIG["custom"]["max_bet_value"]
MIN_BET_VALUE = CONFIG["custom"]["min_bet_value"]
ENABLE_TEST_MODE = CONFIG["custom"]["enable_test_mode"]
