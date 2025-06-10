import psycopg2
import os

# Script para forçar encoding UTF-8 no banco de dados de testes
# Execute: python fix_encoding_schema.py

def fix_encoding():
    db_url = os.getenv("POSTGRES_DATABASE_URL_TEST") or os.getenv("DATABASE_URL_TEST") or "postgresql://postgres:admin@localhost:5432/surebets_test"
    print(f"Conectando em: {db_url}")
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()
    # Força encoding do banco
    cur.execute("ALTER DATABASE surebets_test SET client_encoding TO 'UTF8';")
    # Corrige todas as tabelas para UTF-8
    cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
    for (table,) in cur.fetchall():
        cur.execute(f"ALTER TABLE \"{table}\" OWNER TO postgres;")
    print("Encoding do banco e tabelas ajustado para UTF-8.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    fix_encoding()

# Corrige o encoding do arquivo schema_postgres.sql para UTF-8
with open("backend/database/schema_postgres.sql", "rb") as f:
    raw = f.read()
try:
    text = raw.decode("utf-8")
except UnicodeDecodeError:
    text = raw.decode("latin1")
with open("backend/database/schema_postgres.sql", "w", encoding="utf-8") as f:
    f.write(text)
print("Arquivo corrigido para UTF-8.")
