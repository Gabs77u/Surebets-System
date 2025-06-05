import os
import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / 'config' / 'config.yaml'

def load_config(path: str = None):
    """
    Carrega o arquivo de configuração YAML e retorna um dicionário.
    """
    config_file = path or CONFIG_PATH
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

# Exemplo de uso:
CONFIG = load_config()

# Para acessar: CONFIG['project']['name'], CONFIG['postgres']['host'], etc.
