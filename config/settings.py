import os
import logging
from dotenv import load_dotenv

# Carrega variáveis do .env.production automaticamente em produção
if os.getenv("FLASK_ENV") == "production":
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env.production")
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)

# Configurações gerais do sistema
APP_NAME = "Surebets Hunter Pro"
DEBUG = os.getenv("DEBUG", "False") == "True"
PORT = int(os.getenv("PORT", 8050))

# Configuração para módulos unificados
USE_UNIFIED_MODULES = os.getenv("USE_UNIFIED_MODULES", "True") == "True"
UNIFIED_DASHBOARD_PORT = int(os.getenv("UNIFIED_DASHBOARD_PORT", 8050))
UNIFIED_ADMIN_API_PORT = int(os.getenv("UNIFIED_ADMIN_API_PORT", 5000))

# Configurações de integração
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE", "")

# Configuração de cache
CACHE_TIMEOUT = int(os.getenv("CACHE_TIMEOUT", 60))  # segundos

# Configuração de banco de dados SQLite
DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "..", "backend", "database", "surebets.db"))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")
DATABASE_BACKUP_DIR = os.getenv("DATABASE_BACKUP_DIR", os.path.join(os.path.dirname(__file__), "..", "backend", "database", "backups"))

# Configurações de pool de conexões SQLite
MAX_CONNECTIONS = int(os.getenv("MAX_CONNECTIONS", 10))
CONNECTION_TIMEOUT = float(os.getenv("CONNECTION_TIMEOUT", 30.0))

# Segurança
# IMPORTANTE: Defina uma SECRET_KEY forte e única na sua variável de ambiente para produção!
# Exemplo: openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY and not DEBUG:
    logging.warning("AVISO: SECRET_KEY não definida, usando valor padrão para DEBUG. NÃO USE EM PRODUÇÃO.")
    SECRET_KEY = "debug-secret-key-do-not-use-in-prod"

# IMPORTANTE: Configure ALLOWED_HOSTS explicitamente para seus domínios em produção.
# Exemplo: ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "yourdomain.com,www.yourdomain.com").split(",")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
if not ALLOWED_HOSTS and not DEBUG:
    logging.warning("AVISO: ALLOWED_HOSTS não definido, usando '*' para testes locais. NÃO USE EM PRODUÇÃO.")
    ALLOWED_HOSTS = '*'
ALLOWED_HOSTS = ALLOWED_HOSTS.split(",") if isinstance(ALLOWED_HOSTS, str) and ALLOWED_HOSTS else []

# Nova configuração para a URL da Admin API
ADMIN_API_URL = os.getenv("ADMIN_API_URL", "http://localhost:5000")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")  # hash fixo para testes (senha: admin123)

# Bookmakers
MOCK_BOOKMAKER_DATA = os.getenv("MOCK_BOOKMAKER_DATA", "false").lower() == "true"
BOOKMAKER_TIMEOUT = int(os.getenv("BOOKMAKER_TIMEOUT", 20))
BOOKMAKER_MAX_RETRIES = int(os.getenv("BOOKMAKER_MAX_RETRIES", 5))
BOOKMAKER_RATE_LIMIT = float(os.getenv("BOOKMAKER_RATE_LIMIT", 1.0))
GLOBAL_MIN_ODDS = float(os.getenv("GLOBAL_MIN_ODDS", 1.01))
GLOBAL_MAX_ODDS = float(os.getenv("GLOBAL_MAX_ODDS", 1000))

# APIs específicas
BET365_API_KEY = os.getenv("BET365_API_KEY")
PINNACLE_API_KEY = os.getenv("PINNACLE_API_KEY")
BETFAIR_API_KEY = os.getenv("BETFAIR_API_KEY")
SUPERODDS_API_KEY = os.getenv("SUPERODDS_API_KEY")

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/surebets.log")

# Rate Limiting
RATE_LIMIT = int(os.getenv("RATE_LIMIT", 100))

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
