"""
🗄️ MÓDULO DE BANCO DE DADOS SQLITE
===============================
Sistema de conexão e operações com SQLite para o Surebets System.
Migrado do PostgreSQL para SQLite com melhorias de performance.
"""

import os
import sqlite3
import logging
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from contextlib import contextmanager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações do banco
DATABASE_PATH = os.getenv("SQLITE_DATABASE_PATH", "data/surebets.db")
DATABASE_TIMEOUT = int(os.getenv("DATABASE_TIMEOUT", "30"))

class DatabaseManager:
    """
    Classe principal para gerenciamento de conexões SQLite.

    Features:
    - Pool de conexões thread-safe
    - Transações automáticas
    - Logging detalhado
    - Row factory para resultados como dicionários
    - Backup automático
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern para garantir uma única instância."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializa conexão com SQLite."""
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self._local = threading.local()

        # Criar diretório se não existir
        db_dir = Path(DATABASE_PATH).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        # Inicializar banco
        self._initialize_database()
        logger.info(f"✅ Database SQLite inicializado: {DATABASE_PATH}")

    def _get_connection(self) -> sqlite3.Connection:
        """Obtém conexão thread-local."""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                DATABASE_PATH,
                timeout=DATABASE_TIMEOUT,
                check_same_thread=False,
                isolation_level=None  # Autocommit mode
            )

            # Configurar row factory para resultados como dicionários
            self._local.connection.row_factory = sqlite3.Row

            # Configurações de performance
            self._local.connection.execute("PRAGMA foreign_keys = ON")
            self._local.connection.execute("PRAGMA journal_mode = WAL")
            self._local.connection.execute("PRAGMA synchronous = NORMAL")
            self._local.connection.execute("PRAGMA cache_size = 10000")
            self._local.connection.execute("PRAGMA temp_store = memory")

            # Verificar se foreign keys estão habilitadas
            result = self._local.connection.execute("PRAGMA foreign_keys").fetchone()
            if result[0] != 1:
                logger.warning("⚠️ Foreign keys não foram habilitadas corretamente")

        return self._local.connection

    def _initialize_database(self):
        """Inicializa o schema do banco se necessário."""
        try:
            conn = self._get_connection()

            # Verificar se o banco já foi inicializado
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
            )

            if not cursor.fetchone():
                logger.info("🔨 Criando schema inicial do banco...")
                self._create_schema()
                logger.info("✅ Schema criado com sucesso!")

        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao inicializar banco: {e}")
            raise RuntimeError(f"Erro ao inicializar banco: {e}")

    def _create_schema(self):
        """Cria o schema completo do banco."""
        schema_file = Path(__file__).parent / "schema.sql"

        if schema_file.exists():
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()

            conn = self._get_connection()
            conn.executescript(schema_sql)
        else:
            logger.warning("⚠️ Arquivo schema.sql não encontrado!")

    @contextmanager
    def transaction(self):
        """Context manager para transações."""
        conn = self._get_connection()
        try:
            conn.execute("BEGIN")
            yield conn
            conn.execute("COMMIT")
        except Exception as e:
            conn.execute("ROLLBACK")
            logger.error(f"❌ Erro na transação: {e}")
            raise

    def fetch(self, query: str, params: Optional[Union[tuple, dict]] = None) -> List[sqlite3.Row]:
        """
        Executa SELECT e retorna resultados.

        Args:
            query: SQL query
            params: Parâmetros da query

        Returns:
            Lista de resultados como sqlite3.Row (dict-like)
        """
        try:
            conn = self._get_connection()
            cursor = conn.execute(query, params or ())
            results = cursor.fetchall()

            logger.debug(f"📊 Query executada: {len(results)} registros retornados")
            return results

        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao executar fetch: {e}\nQuery: {query}\nParams: {params}")
            raise

    def fetch_one(self, query: str, params: Optional[Union[tuple, dict]] = None) -> Optional[sqlite3.Row]:
        """
        Executa SELECT e retorna apenas um resultado.

        Args:
            query: SQL query
            params: Parâmetros da query

        Returns:
            Um resultado como sqlite3.Row ou None
        """
        try:
            conn = self._get_connection()
            cursor = conn.execute(query, params or ())
            result = cursor.fetchone()

            logger.debug(f"📊 Query executada: {'1 registro' if result else 'nenhum registro'}")
            return result

        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao executar fetch_one: {e}\nQuery: {query}\nParams: {params}")
            raise

    def execute(self, query: str, params: Optional[Union[tuple, dict]] = None) -> int:
        """
        Executa comandos INSERT/UPDATE/DELETE.

        Args:
            query: SQL query
            params: Parâmetros da query

        Returns:
            Número de linhas afetadas
        """
        try:
            conn = self._get_connection()
            cursor = conn.execute(query, params or ())
            rows_affected = cursor.rowcount

            logger.debug(f"✏️ Query executada: {rows_affected} registros afetados")
            return rows_affected

        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao executar execute: {e}\nQuery: {query}\nParams: {params}")
            raise

    def execute_many(self, query: str, params_list: List[Union[tuple, dict]]) -> int:
        """
        Executa comando com múltiplos conjuntos de parâmetros.

        Args:
            query: SQL query
            params_list: Lista de parâmetros

        Returns:
            Número total de linhas afetadas
        """
        try:
            conn = self._get_connection()
            cursor = conn.executemany(query, params_list)
            rows_affected = cursor.rowcount

            logger.debug(f"✏️ Batch executado: {rows_affected} registros afetados")
            return rows_affected

        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao executar execute_many: {e}\nQuery: {query}")
            raise

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """
        Insere um registro e retorna o ID.

        Args:
            table: Nome da tabela
            data: Dados a inserir

        Returns:
            ID do registro inserido
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = list(data.values())

        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        try:
            conn = self._get_connection()
            cursor = conn.execute(query, values)
            return cursor.lastrowid

        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao inserir em {table}: {e}\nData: {data}")
            raise

    def update(self, table: str, data: Dict[str, Any], where: str, where_params: Union[tuple, dict] = ()) -> int:
        """
        Atualiza registros.

        Args:
            table: Nome da tabela
            data: Dados a atualizar
            where: Cláusula WHERE
            where_params: Parâmetros do WHERE

        Returns:
            Número de registros atualizados
        """
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        values = list(data.values())

        if isinstance(where_params, dict):
            values.extend(where_params.values())
        else:
            values.extend(where_params)

        query = f"UPDATE {table} SET {set_clause} WHERE {where}"

        try:
            conn = self._get_connection()
            cursor = conn.execute(query, values)
            return cursor.rowcount

        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao atualizar {table}: {e}\nData: {data}")
            raise

    def delete(self, table: str, where: str, where_params: Union[tuple, dict] = ()) -> int:
        """
        Deleta registros.

        Args:
            table: Nome da tabela
            where: Cláusula WHERE
            where_params: Parâmetros do WHERE

        Returns:
            Número de registros deletados
        """
        query = f"DELETE FROM {table} WHERE {where}"

        try:
            conn = self._get_connection()
            cursor = conn.execute(query, where_params)
            return cursor.rowcount

        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao deletar de {table}: {e}")
            raise

    def backup(self, backup_path: str = None) -> str:
        """
        Cria backup do banco.

        Args:
            backup_path: Caminho do backup (opcional)

        Returns:
            Caminho do arquivo de backup
        """
        if backup_path is None:
            backup_path = f"{DATABASE_PATH}.backup"

        try:
            source = self._get_connection()
            backup_conn = sqlite3.connect(backup_path)

            source.backup(backup_conn)
            backup_conn.close()

            logger.info(f"💾 Backup criado: {backup_path}")
            return backup_path

        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao criar backup: {e}")
            raise

    def get_table_info(self, table: str) -> List[sqlite3.Row]:
        """Retorna informações sobre a estrutura de uma tabela."""
        return self.fetch(f"PRAGMA table_info({table})")

    def get_tables(self) -> List[str]:
        """Retorna lista de todas as tabelas."""
        results = self.fetch(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        return [row['name'] for row in results]

    def vacuum(self):
        """Executa VACUUM para otimizar o banco."""
        try:
            conn = self._get_connection()
            conn.execute("VACUUM")
            logger.info("🔧 VACUUM executado com sucesso")
        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao executar VACUUM: {e}")
            raise

    def analyze(self):
        """Executa ANALYZE para atualizar estatísticas."""
        try:
            conn = self._get_connection()
            conn.execute("ANALYZE")
            logger.info("📊 ANALYZE executado com sucesso")
        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao executar ANALYZE: {e}")
            raise

    def close(self):
        """Fecha conexões."""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            del self._local.connection
            logger.info("🔒 Conexão fechada")


# Instância global
db = DatabaseManager()

# Funções de conveniência
def get_db() -> DatabaseManager:
    """Retorna instância do banco."""
    return db

def dict_factory(cursor, row):
    """Factory para converter resultados em dicionários."""
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))
