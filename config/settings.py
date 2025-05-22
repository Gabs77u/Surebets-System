import os

# Configurações gerais do sistema
APP_NAME = "Surebets Hunter Pro"
DEBUG = os.getenv("DEBUG", "False") == "True"
PORT = int(os.getenv("PORT", 8050))

# Configurações de integração
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE", "")

# Configuração de cache
CACHE_TIMEOUT = int(os.getenv("CACHE_TIMEOUT", 60))  # segundos

# Configuração de banco de dados
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://user:password@localhost:5432/surebets")

# Segurança
SECRET_KEY = os.getenv("SECRET_KEY", "troque-esta-chave")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
