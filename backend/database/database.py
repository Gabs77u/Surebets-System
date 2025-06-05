"""
🗄️ MÓDULO DE BANCO DE DADOS POSTGRESQL
===============================
Sistema de conexão e operações com PostgreSQL para o Surebets System.
"""

import os
import psycopg2
import psycopg2.extras
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
DATABASE_URL = os.getenv("POSTGRES_DATABASE_URL", "dbname=surebets user=postgres password=postgres host=localhost port=5432")

class PostgresDatabaseManager:
    """
    Classe principal para gerenciamento de conexões PostgreSQL.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(PostgresDatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self._local = threading.local()
        self._initialize_database()
        logger.info(f"✅ Database PostgreSQL inicializado: {DATABASE_URL}")

    def _get_connection(self) -> psycopg2.extensions.connection:
        if not hasattr(self._local, 'connection'):
            self._local.connection = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
        return self._local.connection

    def _initialize_database(self):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT to_regclass('public.users')")
            if cursor.fetchone()[0] is None:
                logger.info("🔨 Criando schema inicial do banco PostgreSQL...")
                self._create_schema()
                logger.info("✅ Schema criado com sucesso!")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco: {e}")
            raise RuntimeError(f"Erro ao inicializar banco: {e}")

    def _create_schema(self):
        schema_file = Path(__file__).parent / "schema_postgres.sql"
        if schema_file.exists():
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute(schema_sql)
            conn.commit()
        else:
            logger.warning("⚠️ Arquivo schema_postgres.sql não encontrado!")

    @contextmanager
    def transaction(self):
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro na transação: {e}")
            raise

    def fetch(self, query: str, params: Optional[Union[tuple, dict]] = None) -> List[Dict[str, Any]]:
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
            logger.debug(f"📊 Query executada: {len(results)} registros retornados")
            return results
        except Exception as e:
            logger.error(f"❌ Erro ao executar fetch: {e}\nQuery: {query}\nParams: {params}")
            raise

    def fetch_one(self, query: str, params: Optional[Union[tuple, dict]] = None) -> Optional[Dict[str, Any]]:
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
            logger.debug(f"📊 Query executada: {'1 registro' if result else 'nenhum registro'}")
            return result
        except Exception as e:
            logger.error(f"❌ Erro ao executar fetch_one: {e}\nQuery: {query}\nParams: {params}")
            raise

    def execute(self, query: str, params: Optional[Union[tuple, dict]] = None) -> int:
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                rows_affected = cursor.rowcount
            conn.commit()
            logger.debug(f"✏️ Query executada: {rows_affected} registros afetados")
            return rows_affected
        except Exception as e:
            logger.error(f"❌ Erro ao executar execute: {e}\nQuery: {query}\nParams: {params}")
            raise

    def execute_many(self, query: str, params_list: List[Union[tuple, dict]]) -> int:
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.executemany(query, params_list)
                rows_affected = cursor.rowcount
            conn.commit()
            logger.debug(f"✏️ Batch executado: {rows_affected} registros afetados")
            return rows_affected
        except Exception as e:
            logger.error(f"❌ Erro ao executar execute_many: {e}\nQuery: {query}")
            raise

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        columns = ', '.join(data.keys())
        placeholders = ', '.join([f'%s' for _ in data])
        values = list(data.values())
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING id"
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                inserted_id = cursor.fetchone()["id"]
            conn.commit()
            return inserted_id
        except Exception as e:
            logger.error(f"❌ Erro ao inserir em {table}: {e}\nData: {data}")
            raise

    def update(self, table: str, data: Dict[str, Any], where: str, where_params: Union[tuple, dict] = ()) -> int:
        set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
        values = list(data.values())
        if isinstance(where_params, dict):
            values.extend(where_params.values())
        else:
            values.extend(where_params)
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                rows_affected = cursor.rowcount
            conn.commit()
            return rows_affected
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar {table}: {e}\nData: {data}")
            raise

    def delete(self, table: str, where: str, where_params: Union[tuple, dict] = ()) -> int:
        query = f"DELETE FROM {table} WHERE {where}"
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, where_params)
                rows_affected = cursor.rowcount
            conn.commit()
            return rows_affected
        except Exception as e:
            logger.error(f"❌ Erro ao deletar de {table}: {e}")
            raise

    def get_tables(self) -> List[str]:
        results = self.fetch(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
        return [row['table_name'] for row in results]

    def analyze(self):
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute("ANALYZE")
            conn.commit()
            logger.info("📊 ANALYZE executado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao executar ANALYZE: {e}")
            raise

    def close(self):
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            del self._local.connection
            logger.info("🔒 Conexão fechada")

# Instância global
pg_db = PostgresDatabaseManager()

def get_pg_db() -> PostgresDatabaseManager:
    return pg_db
