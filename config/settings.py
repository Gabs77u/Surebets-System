import os

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
DATABASE_BACKUP_DIR = os.getenv("DATABASE_BACKUP_DIR", os.path.join(os.path.dirname(__file__), "..", "backend", "database", "backups"))

# Configurações de pool de conexões SQLite
MAX_CONNECTIONS = int(os.getenv("MAX_CONNECTIONS", 10))
CONNECTION_TIMEOUT = float(os.getenv("CONNECTION_TIMEOUT", 30.0))

# Segurança
# IMPORTANTE: Defina uma SECRET_KEY forte e única na sua variável de ambiente para produção!
# Exemplo: openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY and not DEBUG:
    raise ValueError("A SECRET_KEY deve ser definida em variáveis de ambiente para produção.")
if DEBUG and not SECRET_KEY:
    print("AVISO: SECRET_KEY não definida, usando valor padrão para DEBUG. NÃO USE EM PRODUÇÃO.")
    SECRET_KEY = "debug-secret-key-do-not-use-in-prod"


# IMPORTANTE: Configure ALLOWED_HOSTS explicitamente para seus domínios em produção.
# Exemplo: ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "yourdomain.com,www.yourdomain.com").split(",")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "")
if not ALLOWED_HOSTS and not DEBUG:
    raise ValueError("ALLOWED_HOSTS deve ser definido em variáveis de ambiente para produção.")
if ALLOWED_HOSTS == "*":
    print("AVISO: ALLOWED_HOSTS está configurado como '*' o que é inseguro para produção.")
ALLOWED_HOSTS = ALLOWED_HOSTS.split(",") if ALLOWED_HOSTS else []

# Nova configuração para a URL da Admin API
ADMIN_API_URL = os.getenv("ADMIN_API_URL", "http://localhost:5000")
