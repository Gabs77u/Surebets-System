# ⚙️ Configurações do Sistema de Surebets
# Copie este arquivo para settings.py e ajuste conforme necessário

import os
from datetime import timedelta

# =============================================================================
# CONFIGURAÇÕES BÁSICAS
# =============================================================================

# Configurações do Flask
class Config:
    """Configurações base para todas as environments"""
    
    # Chave secreta para sessões e CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuração do banco de dados
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///surebets.db'
    
    # Configurações de debug
    DEBUG = False
    TESTING = False
    
    # Configurações de CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

class DevelopmentConfig(Config):
    """Configurações para ambiente de desenvolvimento"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Configurações para ambiente de produção"""
    DEBUG = False
    # Em produção, sempre use variáveis de ambiente para secrets
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY deve ser definida em produção")

class TestingConfig(Config):
    """Configurações para testes"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    DATABASE_URL = 'sqlite:///:memory:'

# =============================================================================
# CONFIGURAÇÕES DO SISTEMA DE ARBITRAGEM
# =============================================================================

ARBITRAGE_SETTINGS = {
    # Configurações de detecção
    'min_profit': 2.0,              # Lucro mínimo para arbitragem (%)
    'max_profit': 50.0,             # Lucro máximo considerado válido (%)
    'min_stake': 10.0,              # Aposta mínima
    'max_stake': 1000.0,            # Aposta máxima
    
    # Configurações de timing
    'check_interval': 30,           # Intervalo entre verificações (segundos)
    'cache_duration': 300,          # Duração do cache de odds (segundos)
    'request_timeout': 10,          # Timeout para requisições HTTP
    
    # Configurações de filtros
    'enabled_sports': [
        'football', 'basketball', 'tennis', 
        'soccer', 'baseball', 'hockey'
    ],
    'enabled_markets': [
        'match_winner', 'over_under', 'handicap',
        'both_teams_score', 'correct_score'
    ],
    
    # Configurações de qualidade
    'min_bookmakers': 2,            # Mínimo de casas para arbitragem
    'max_age_hours': 2,             # Idade máxima das odds (horas)
    'confidence_threshold': 0.8,    # Threshold de confiança
}

# =============================================================================
# CONFIGURAÇÕES DOS BOOKMAKERS
# =============================================================================

BOOKMAKER_SETTINGS = {
    # APIs disponíveis
    'enabled_adapters': [
        'bet365', 'betfair', 'pinnacle', 
        'william_hill', 'betway', '1xbet'
    ],
    
    # Configurações de rate limiting
    'rate_limits': {
        'bet365': {'requests': 100, 'window': 3600},
        'betfair': {'requests': 200, 'window': 3600},
        'pinnacle': {'requests': 500, 'window': 3600},
        'default': {'requests': 100, 'window': 3600}
    },
    
    # Timeouts específicos
    'timeouts': {
        'bet365': 15,
        'betfair': 10,
        'pinnacle': 5,
        'default': 10
    },
    
    # Configurações de retry
    'retry_settings': {
        'max_attempts': 3,
        'backoff_factor': 1.5,
        'retry_codes': [429, 500, 502, 503, 504]
    }
}

# =============================================================================
# CONFIGURAÇÕES DE CACHE
# =============================================================================

CACHE_SETTINGS = {
    # Configurações do Redis
    'redis_url': os.environ.get('REDIS_URL') or 'redis://localhost:6379/0',
    'default_timeout': 300,         # 5 minutos
    
    # Cache específico por tipo
    'cache_timeouts': {
        'odds': 60,                 # 1 minuto
        'events': 300,              # 5 minutos
        'bookmakers': 1800,         # 30 minutos
        'user_sessions': 3600,      # 1 hora
        'api_responses': 120,       # 2 minutos
    },
    
    # Configurações de cache local (fallback)
    'local_cache': {
        'enabled': True,
        'max_size': 1000,
        'timeout': 60
    }
}

# =============================================================================
# CONFIGURAÇÕES DE NOTIFICAÇÕES
# =============================================================================

NOTIFICATION_SETTINGS = {
    # Tipos de notificação habilitados
    'email_enabled': os.environ.get('EMAIL_ENABLED', 'false').lower() == 'true',
    'sms_enabled': os.environ.get('SMS_ENABLED', 'false').lower() == 'true',
    'webhook_enabled': True,
    'desktop_enabled': True,
    
    # Configurações de email
    'email': {
        'smtp_server': os.environ.get('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': int(os.environ.get('SMTP_PORT', '587')),
        'username': os.environ.get('EMAIL_USERNAME'),
        'password': os.environ.get('EMAIL_PASSWORD'),
        'use_tls': True,
        'from_address': os.environ.get('FROM_EMAIL', 'noreply@surebets.com')
    },
    
    # Configurações de SMS
    'sms': {
        'provider': 'twilio',  # ou 'aws_sns'
        'api_key': os.environ.get('SMS_API_KEY'),
        'api_secret': os.environ.get('SMS_API_SECRET'),
        'from_number': os.environ.get('SMS_FROM_NUMBER')
    },
    
    # Configurações de webhook
    'webhook': {
        'url': os.environ.get('WEBHOOK_URL'),
        'secret': os.environ.get('WEBHOOK_SECRET'),
        'timeout': 10,
        'retry_attempts': 3
    },
    
    # Configurações de frequência
    'frequency': {
        'max_per_hour': 10,         # Máximo de notificações por hora
        'cooldown_minutes': 5,      # Cooldown entre notificações similares
        'batch_delay_seconds': 30   # Delay para agrupar notificações
    }
}

# =============================================================================
# CONFIGURAÇÕES DE LOGGING
# =============================================================================

LOGGING_SETTINGS = {
    # Nível de log
    'level': os.environ.get('LOG_LEVEL', 'INFO'),
    
    # Arquivos de log
    'files': {
        'main': 'logs/surebets.log',
        'error': 'logs/error.log',
        'access': 'logs/access.log',
        'arbitrage': 'logs/arbitrage.log'
    },
    
    # Configurações de rotação
    'rotation': {
        'max_bytes': 10 * 1024 * 1024,  # 10MB
        'backup_count': 5,
        'encoding': 'utf-8'
    },
    
    # Formatação
    'format': {
        'detailed': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        'simple': '%(asctime)s - %(levelname)s - %(message)s'
    },
    
    # Loggers específicos
    'loggers': {
        'arbitrage': {'level': 'DEBUG', 'file': 'arbitrage'},
        'bookmaker': {'level': 'INFO', 'file': 'main'},
        'notification': {'level': 'INFO', 'file': 'main'},
        'api': {'level': 'INFO', 'file': 'access'}
    }
}

# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA
# =============================================================================

SECURITY_SETTINGS = {
    # Rate limiting
    'rate_limiting': {
        'enabled': True,
        'default_rate': '100/hour',
        'api_rate': '1000/hour',
        'admin_rate': '50/hour'
    },
    
    # Autenticação
    'auth': {
        'session_timeout': 3600,    # 1 hora
        'max_login_attempts': 5,
        'lockout_duration': 900,    # 15 minutos
        'password_min_length': 8,
        'require_2fa': False
    },
    
    # CORS
    'cors': {
        'origins': os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(','),
        'methods': ['GET', 'POST', 'PUT', 'DELETE'],
        'allow_headers': ['Content-Type', 'Authorization']
    },
    
    # Headers de segurança
    'security_headers': {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
}

# =============================================================================
# CONFIGURAÇÕES DE MONITORAMENTO
# =============================================================================

MONITORING_SETTINGS = {
    # Health checks
    'health_checks': {
        'database': True,
        'redis': True,
        'external_apis': True,
        'disk_space': True,
        'memory_usage': True
    },
    
    # Métricas
    'metrics': {
        'enabled': True,
        'endpoint': '/metrics',
        'include_default': True,
        'custom_metrics': [
            'arbitrage_opportunities_found',
            'api_requests_total',
            'notification_sent_total',
            'error_rate'
        ]
    },
    
    # Alertas
    'alerts': {
        'error_rate_threshold': 0.05,      # 5%
        'response_time_threshold': 1.0,    # 1 segundo
        'memory_usage_threshold': 0.8,     # 80%
        'disk_usage_threshold': 0.9        # 90%
    }
}

# =============================================================================
# CONFIGURAÇÕES DE INTERNACIONALIZAÇÃO
# =============================================================================

I18N_SETTINGS = {
    'default_language': 'pt-br',
    'supported_languages': ['pt-br', 'en'],
    'fallback_language': 'en',
    'auto_detect': True,
    'cookie_name': 'language',
    'cookie_max_age': 30 * 24 * 3600  # 30 dias
}

# =============================================================================
# CONFIGURAÇÕES DE DESENVOLVIMENTO
# =============================================================================

DEVELOPMENT_SETTINGS = {
    # Hot reload
    'hot_reload': True,
    
    # Debugging
    'debug_toolbar': False,
    'profiler': False,
    
    # Mock data
    'use_mock_apis': True,
    'mock_data_file': 'data/mock_odds.json',
    
    # Testing
    'test_mode': False,
    'test_database': 'sqlite:///test.db'
}

# =============================================================================
# SELEÇÃO DE CONFIGURAÇÃO POR AMBIENTE
# =============================================================================

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Ambiente atual
ENVIRONMENT = os.environ.get('FLASK_ENV', 'development')
Config = config.get(ENVIRONMENT, config['default'])

# =============================================================================
# VALIDAÇÃO DE CONFIGURAÇÕES
# =============================================================================

def validate_config():
    """Valida se todas as configurações necessárias estão presentes"""
    errors = []
    
    # Validar configurações obrigatórias para produção
    if ENVIRONMENT == 'production':
        required_env_vars = [
            'SECRET_KEY',
            'DATABASE_URL'
        ]
        
        for var in required_env_vars:
            if not os.environ.get(var):
                errors.append(f"Variável de ambiente obrigatória não definida: {var}")
    
    # Validar configurações de arbitragem
    if ARBITRAGE_SETTINGS['min_profit'] >= ARBITRAGE_SETTINGS['max_profit']:
        errors.append("min_profit deve ser menor que max_profit")
    
    if ARBITRAGE_SETTINGS['min_stake'] >= ARBITRAGE_SETTINGS['max_stake']:
        errors.append("min_stake deve ser menor que max_stake")
    
    # Validar configurações de cache
    if CACHE_SETTINGS['default_timeout'] <= 0:
        errors.append("default_timeout do cache deve ser maior que 0")
    
    return errors

# Executar validação na importação
validation_errors = validate_config()
if validation_errors:
    for error in validation_errors:
        print(f"ERRO DE CONFIGURAÇÃO: {error}")
    
    if ENVIRONMENT == 'production':
        raise ValueError("Configurações inválidas para produção")

# =============================================================================
# CONFIGURAÇÕES DERIVADAS
# =============================================================================

# Configurações derivadas baseadas no ambiente
if ENVIRONMENT == 'production':
    # Em produção, logs mais verbosos e cache mais agressivo
    LOGGING_SETTINGS['level'] = 'INFO'
    CACHE_SETTINGS['default_timeout'] = 600
    DEVELOPMENT_SETTINGS['use_mock_apis'] = False
else:
    # Em desenvolvimento, mais debugging e menos cache
    LOGGING_SETTINGS['level'] = 'DEBUG'
    CACHE_SETTINGS['default_timeout'] = 60
    DEVELOPMENT_SETTINGS['use_mock_apis'] = True

# Exportar todas as configurações
__all__ = [
    'Config', 'DevelopmentConfig', 'ProductionConfig', 'TestingConfig',
    'ARBITRAGE_SETTINGS', 'BOOKMAKER_SETTINGS', 'CACHE_SETTINGS',
    'NOTIFICATION_SETTINGS', 'LOGGING_SETTINGS', 'SECURITY_SETTINGS',
    'MONITORING_SETTINGS', 'I18N_SETTINGS', 'DEVELOPMENT_SETTINGS',
    'ENVIRONMENT', 'validate_config'
]
