"""
🧪 MÓDULO DE TESTES - SISTEMA DE SUREBETS
========================================
Configuração e utilitários para testes do sistema.
"""

# Todas as configurações de banco de dados de teste agora usam PostgreSQL via fixtures em conftest.py
# Não é mais necessário configurar SQLite aqui.

import os
import sys
from pathlib import Path

# Adicionar o diretório backend ao path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Configurar ambiente de teste
os.environ["TESTING"] = "True"
