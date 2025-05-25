import os
import psycopg2
from psycopg2.extras import RealDictCursor

POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://user:password@localhost:5432/surebets")

class Database:
    def __init__(self):
        """Inicializa conexão com o banco de dados PostgreSQL."""
        try:
            self.conn = psycopg2.connect(POSTGRES_URL, cursor_factory=RealDictCursor)
            self.cur = self.conn.cursor()
        except Exception as e:
            raise RuntimeError(f"Erro ao conectar ao banco de dados: {e}")

    def fetch(self, query: str, params=None):
        """Executa SELECT e retorna resultados."""
        self.cur.execute(query, params or ())
        return self.cur.fetchall()

    def execute(self, query: str, params=None):
        """Executa comandos INSERT/UPDATE/DELETE."""
        self.cur.execute(query, params or ())
        self.conn.commit()

    def close(self):
        """Fecha a conexão com o banco de dados."""
        self.cur.close()
        self.conn.close()
