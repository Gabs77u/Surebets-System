"""
🧪 CONFIGURAÇÃO DE TESTES - PYTEST
==================================
Fixtures e configurações globais para todos os testes.
"""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch

# Importar módulos do sistema
from database.database import DatabaseManager, get_db


@pytest.fixture(scope="session")
def test_database_path():
    """Cria um banco temporário para testes."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        yield f.name
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture(scope="function")
def clean_database(test_database_path):
    """Fixture que fornece um banco limpo para cada teste."""
    # Configurar banco de teste ANTES de importar o DatabaseManager
    import os
    os.environ['SQLITE_DATABASE_PATH'] = test_database_path
    
    # Limpar cache do singleton para testes
    DatabaseManager._instance = None
    
    # Criar instância limpa do banco
    db = DatabaseManager()
    
    # Para testes de threading, usar WAL mode com shared cache
    conn = db._get_connection()
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA cache = shared")
    
    # Forçar criação do schema se necessário
    schema_file = Path(__file__).parent.parent / "database" / "schema.sql"
    if schema_file.exists():
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        try:
            # Verificar se tabelas já existem
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
            if not cursor.fetchone():
                conn.executescript(schema_sql)
                conn.commit()
        except Exception as e:
            print(f"Erro ao criar schema: {e}")
            # Se falhou, tentar executar script completo novamente
            conn.executescript(schema_sql)
            conn.commit()
    
    yield db
    
    # Limpeza após teste
    if hasattr(db, 'close'):
        db.close()
    
    # Limpar variável de ambiente
    if 'SQLITE_DATABASE_PATH' in os.environ:
        del os.environ['SQLITE_DATABASE_PATH']


@pytest.fixture(scope="function")
def populated_database(clean_database):
    """Fixture que fornece um banco com dados de teste."""
    db = clean_database
    
    # Verificar se as tabelas foram criadas
    conn = db._get_connection()
    try:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tabelas disponíveis: {tables}")
        
        # Inserir dados de teste
        populate_file = Path(__file__).parent.parent / "database" / "populate.sql"
        if populate_file.exists():
            with open(populate_file, 'r', encoding='utf-8') as f:
                populate_sql = f.read()
            
            conn.executescript(populate_sql)
            conn.commit()
            
            # Verificar se os dados foram inseridos
            cursor = conn.execute("SELECT COUNT(*) as count FROM events")
            event_count = cursor.fetchone()[0]
            print(f"Eventos inseridos: {event_count}")
            
    except Exception as e:
        print(f"Erro ao popular banco: {e}")
        raise
    
    yield db


@pytest.fixture
def sample_bookmaker():
    """Dados de exemplo para bookmaker."""
    return {
        'name': 'Test Bookmaker',
        'api_url': 'https://api.testbookmaker.com',
        'rate_limit': 100,
        'timeout_seconds': 15,
        'is_active': True
    }


@pytest.fixture
def sample_sport():
    """Dados de exemplo para esporte."""
    return {
        'name': 'Futebol de Teste',
        'slug': 'test-football',
        'is_active': True
    }


@pytest.fixture
def sample_league(populated_database):
    """Dados de exemplo para liga."""
    return {
        'sport_id': 1,  # Assume que existe um esporte com ID 1
        'name': 'Liga de Teste',
        'slug': 'test-league',
        'country': 'Brasil',
        'is_active': True
    }


@pytest.fixture
def sample_event(populated_database):
    """Dados de exemplo para evento."""
    return {
        'external_id': 'TEST_EVT_001',
        'league_id': 1,  # Assume que existe uma liga com ID 1
        'home_team': 'Time Casa',
        'away_team': 'Time Visitante',
        'start_time': '2025-06-01 15:00:00',
        'status': 'upcoming',
        'is_active': True
    }


@pytest.fixture
def sample_selection(populated_database):
    """Dados de exemplo para seleção."""
    return {
        'event_id': 1001,  # Assume que existe um evento
        'market_id': 1,    # Assume que existe um mercado
        'bookmaker_id': 1, # Assume que existe um bookmaker
        'name': 'Vitória Time Casa',
        'odds': 2.50,
        'is_active': True
    }


@pytest.fixture
def sample_user():
    """Dados de exemplo para usuário."""
    return {
        'username': 'test_user',
        'email': 'test@example.com',
        'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewQ3V8Yb5mQNXkkG',
        'first_name': 'Test',
        'last_name': 'User',
        'is_active': True,
        'is_admin': False,
        'email_verified': True
    }


@pytest.fixture
def sample_arbitrage_opportunity(populated_database):
    """Dados de exemplo para oportunidade de arbitragem."""
    return {
        'event_id': 1001,
        'market_id': 1,
        'profit_percentage': 5.5,
        'total_implied_probability': 94.5,
        'stakes_json': '{"stakes":[{"bookmaker":"Test","selection":"Home","amount":500,"percentage":50}]}',
        'selections_json': '{"selections":[{"bookmaker":"Test","selection":"Home","odds":2.0}]}',
        'is_active': True,
        'expires_at': '2025-06-01 14:50:00',
        'detected_at': '2025-05-30 14:00:00'
    }


@pytest.fixture
def mock_api_response():
    """Mock para respostas de API externa."""
    return {
        'status': 'success',
        'data': {
            'events': [
                {
                    'id': 'ext_001',
                    'home_team': 'Team A',
                    'away_team': 'Team B',
                    'start_time': '2025-06-01T15:00:00Z',
                    'odds': {
                        'home': 2.10,
                        'draw': 3.30,
                        'away': 3.50
                    }
                }
            ]
        }
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


@pytest.fixture(scope="function")
def threading_database(test_database_path):
    """Fixture específica para testes de threading com conexão compartilhada."""
    import os
    import threading
    
    # Configurar banco de teste
    os.environ['SQLITE_DATABASE_PATH'] = test_database_path
    
    # Limpar cache do singleton para testes
    DatabaseManager._instance = None
    
    # Criar uma instância modificada para suportar threading
    class ThreadSafeDatabaseManager(DatabaseManager):
        def __init__(self):
            """Inicializar com conexão única para threading."""
            self._initialized = True
            self._lock = threading.RLock()
            
            # Criar conexão única compartilhada
            self._shared_connection = sqlite3.connect(
                test_database_path,
                timeout=30,
                check_same_thread=False,
                isolation_level=None
            )
            
            # Configurar para uso compartilhado
            self._shared_connection.row_factory = sqlite3.Row
            self._shared_connection.execute("PRAGMA foreign_keys = ON")
            self._shared_connection.execute("PRAGMA journal_mode = WAL")
            self._shared_connection.execute("PRAGMA synchronous = NORMAL")
            self._shared_connection.execute("PRAGMA cache_size = 10000")
            self._shared_connection.execute("PRAGMA temp_store = memory")
            
        def _get_connection(self):
            """Retornar sempre a mesma conexão para threading."""
            return self._shared_connection
            
        def fetch(self, query: str, params=None):
            """Thread-safe fetch."""
            with self._lock:
                return super().fetch(query, params)
                
        def execute(self, query: str, params=None):
            """Thread-safe execute."""
            with self._lock:
                return super().execute(query, params)
        
        def close(self):
            """Fechar conexão compartilhada."""
            if hasattr(self, '_shared_connection'):
                self._shared_connection.close()
    
    # Criar instância thread-safe
    db = ThreadSafeDatabaseManager()
    
    # Criar schema
    schema_file = Path(__file__).parent.parent / "database" / "schema.sql"
    if schema_file.exists():
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        conn = db._get_connection()
        conn.executescript(schema_sql)
        conn.commit()
    
    # Inserir dados de teste
    populate_file = Path(__file__).parent.parent / "database" / "populate.sql"
    if populate_file.exists():
        with open(populate_file, 'r', encoding='utf-8') as f:
            populate_sql = f.read()
        
        conn = db._get_connection()
        conn.executescript(populate_sql)
        conn.commit()
    
    yield db
    
    # Limpeza
    db.close()
    
    # Limpar variável de ambiente
    if 'SQLITE_DATABASE_PATH' in os.environ:
        del os.environ['SQLITE_DATABASE_PATH']


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
