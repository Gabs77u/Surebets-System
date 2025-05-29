"""
🧪 MÓDULO DE TESTES - SISTEMA DE SUREBETS
========================================
Configuração e utilitários para testes do sistema.
"""

import os
import sys
import tempfile
import sqlite3
from pathlib import Path

# Adicionar o diretório backend ao path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Configurar ambiente de teste
os.environ['SQLITE_DATABASE_PATH'] = ':memory:'  # Banco em memória para testes
os.environ['TESTING'] = 'True'
