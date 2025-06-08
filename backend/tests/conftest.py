"""
🧪 CONFIGURAÇÃO DE TESTES - PYTEST
==================================
Fixtures e configurações globais para todos os testes.
"""

import pytest
import os
from backend.database.database import get_db
from pathlib import Path


@pytest.fixture(scope="session")
def test_database_url():
    """Retorna a URL do banco PostgreSQL de teste."""
    return os.getenv("POSTGRES_DATABASE_URL") or os.getenv("DATABASE_URL")


@pytest.fixture(scope="function")
def clean_database(test_database_url):
    """Fixture que fornece um banco limpo para cada teste usando PostgreSQL."""
    db = get_db()
    conn = db._get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        tables = [row["tablename"] for row in cursor.fetchall()]
        for table in tables:
            cursor.execute(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE')
    conn.commit()
    # Recriar schema se necessário
    schema_file = Path(__file__).parent.parent / "database" / "schema_postgres.sql"
    if schema_file.exists():
        with open(schema_file, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        with conn.cursor() as cursor:
            cursor.execute(schema_sql)
        conn.commit()
    # Popular banco com dados fictícios
    populate_file = Path(__file__).parent.parent / "database" / "populate.sql"
    if populate_file.exists():
        with open(populate_file, "r", encoding="utf-8") as f:
            populate_sql = f.read()
        # Executa cada comando separadamente, ignorando linhas em branco
        statements = [stmt.strip() for stmt in populate_sql.split(";") if stmt.strip()]
        with conn.cursor() as cursor:
            for stmt in statements:
                cursor.execute(stmt)
        conn.commit()
    yield db
    db.close()


@pytest.fixture(scope="function")
def populated_database(clean_database):
    """Fixture que fornece um banco com dados de teste."""
    return clean_database


@pytest.fixture
def sample_bookmaker():
    """Dados de exemplo para bookmaker."""
    return {
        "name": "Test Bookmaker",
        "api_url": "https://api.testbookmaker.com",
        "rate_limit": 100,
        "timeout_seconds": 15,
        "is_active": True,
    }


@pytest.fixture
def sample_sport():
    """Dados de exemplo para esporte."""
    return {"name": "Futebol de Teste", "slug": "test-football", "is_active": True}


@pytest.fixture
def sample_league(populated_database):
    """Dados de exemplo para liga."""
    return {
        "sport_id": 1,  # Assume que existe um esporte com ID 1
        "name": "Liga de Teste",
        "slug": "test-league",
        "country": "Brasil",
        "is_active": True,
    }


@pytest.fixture
def sample_event(populated_database):
    """Dados de exemplo para evento."""
    return {
        "external_id": "TEST_EVT_001",
        "league_id": 1,  # Assume que existe uma liga com ID 1
        "home_team": "Time Casa",
        "away_team": "Time Visitante",
        "start_time": "2025-06-01 15:00:00",
        "status": "upcoming",
        "is_active": True,
    }


@pytest.fixture
def sample_selection(populated_database):
    """Dados de exemplo para seleção."""
    return {
        "event_id": 1001,  # Assume que existe um evento
        "market_id": 1,  # Assume que existe um mercado
        "bookmaker_id": 1,  # Assume que existe um bookmaker
        "name": "Vitória Time Casa",
        "odds": 2.50,
        "is_active": True,
    }


@pytest.fixture
def sample_user():
    """Dados de exemplo para usuário."""
    return {
        "username": "test_user",
        "email": "test@example.com",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewQ3V8Yb5mQNXkkG",
        "first_name": "Test",
        "last_name": "User",
        "is_active": True,
        "is_admin": False,
        "email_verified": True,
    }


@pytest.fixture
def sample_arbitrage_opportunity(populated_database):
    """Dados de exemplo para oportunidade de arbitragem."""
    return {
        "event_id": 1001,
        "market_id": 1,
        "profit_percentage": 5.5,
        "total_implied_probability": 94.5,
        "stakes_json": '{"stakes":[{"bookmaker":"Test","selection":"Home","amount":500,"percentage":50}]}',
        "selections_json": '{"selections":[{"bookmaker":"Test","selection":"Home","odds":2.0}]}',
        "is_active": True,
        "expires_at": "2025-06-01 14:50:00",
        "detected_at": "2025-05-30 14:00:00",
    }


@pytest.fixture
def mock_api_response():
    """Mock para respostas de API externa."""
    return {
        "status": "success",
        "data": {
            "events": [
                {
                    "id": "ext_001",
                    "home_team": "Team A",
                    "away_team": "Team B",
                    "start_time": "2025-06-01T15:00:00Z",
                    "odds": {"home": 2.10, "draw": 3.30, "away": 3.50},
                }
            ]
        },
    }


@pytest.fixture
def benchmark_timer():
    """Fixture para medir tempo de execução em testes de performance."""
    import time

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = time.perf_counter()

        def stop(self):
            self.end_time = time.perf_counter()

        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None

        def elapsed_ms(self):
            elapsed = self.elapsed
            return elapsed * 1000 if elapsed else None

    return Timer()


@pytest.fixture
def memory_profiler():
    """Fixture para monitorar uso de memória."""
    import psutil
    import os

    class MemoryProfiler:
        def __init__(self):
            self.process = psutil.Process(os.getpid())
            self.initial_memory = None
            self.peak_memory = None

        def start(self):
            self.initial_memory = self.process.memory_info().rss

        def get_current_memory(self):
            return self.process.memory_info().rss

        def get_memory_usage(self):
            current = self.get_current_memory()
            if self.initial_memory:
                return current - self.initial_memory
            return current

        def get_memory_usage_mb(self):
            usage = self.get_memory_usage()
            return usage / (1024 * 1024) if usage else None

    return MemoryProfiler()


# Configurações globais do pytest
def pytest_configure(config):
    """Configuração global do pytest."""
    import warnings

    warnings.filterwarnings("ignore", category=DeprecationWarning)


def pytest_collection_modifyitems(config, items):
    """Modificar itens coletados para adicionar marcadores."""
    for item in items:
        # Adicionar marcadores baseados no caminho do arquivo
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        elif "stress" in str(item.fspath):
            item.add_marker(pytest.mark.stress)
