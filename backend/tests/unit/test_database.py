"""Testes unitários para o módulo DatabaseManager."""

import pytest


def test_simple():
    """Teste simples para verificar se pytest funciona."""
    assert True


class TestDatabaseConnection:
    """Testes de conexão e inicialização do banco."""
    
    def test_basic_import(self):
        from backend.database.database_postgres import PostgresDatabaseManager
        assert PostgresDatabaseManager is not None
