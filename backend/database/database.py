import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Any, Dict

POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://user:password@localhost:5432/surebets")

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(POSTGRES_URL, cursor_factory=RealDictCursor)
        self.cur = self.conn.cursor()

    def fetch(self, query: str, params=None):
        self.cur.execute(query, params or ())
        return self.cur.fetchall()

    def execute(self, query: str, params=None):
        self.cur.execute(query, params or ())
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()

# Exemplo de uso de cache simples em memória
class SimpleCache:
    def __init__(self):
        self.cache: Dict[str, Any] = {}

    def get(self, key: str):
        return self.cache.get(key)

    def set(self, key: str, value: Any):
        self.cache[key] = value

    def clear(self):
        self.cache = {}
