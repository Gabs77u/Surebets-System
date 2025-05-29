"""Testes unitários para o módulo DatabaseManager."""

import pytest


def test_simple():
    """Teste simples para verificar se pytest funciona."""
    assert True


class TestDatabaseConnection:
    """Testes de conexão e inicialização do banco."""
    
    def test_basic_import(self):
        """Testa import básico."""
        from database.database import DatabaseManager
        assert DatabaseManager is not None
