import subprocess
import sys
import os
from pathlib import Path

# Caminhos relativos robustos
BASE_DIR = Path(__file__).parent.resolve()
BACKEND_DIR = BASE_DIR / "backend"
SRC_DATA_DIR = BASE_DIR / "src" / "data"
DB_SCHEMA = BACKEND_DIR / "database" / "schema.sql"

DASH_PATH = str(BACKEND_DIR / "app.py")
ADMIN_API_PATH = str(BACKEND_DIR / "admin_api.py")

processes = []

def init_database():
    import psycopg2
    import time
    from config import settings
    print("Aguardando banco de dados PostgreSQL...")
    for _ in range(30):
        try:
            conn = psycopg2.connect(settings.POSTGRES_URL)
            cur = conn.cursor()
            with open(DB_SCHEMA, "r", encoding="utf-8") as f:
                cur.execute(f.read())
            conn.commit()
            cur.close()
            conn.close()
            print("Banco de dados inicializado!")
            return
        except Exception as e:
            print("Aguardando DB...", e)
            time.sleep(2)
    print("Não foi possível conectar ao banco de dados.")
    sys.exit(1)

def run_dash():
    env = os.environ.copy()
    env["STATIC_DATA"] = str(SRC_DATA_DIR)
    return subprocess.Popen([sys.executable, DASH_PATH], env=env)

def run_admin_api():
    env = os.environ.copy()
    env["STATIC_DATA"] = str(SRC_DATA_DIR)
    return subprocess.Popen([sys.executable, ADMIN_API_PATH], env=env)

if __name__ == "__main__":
    print("Iniciando Surebets System...")
    print("Se o antivírus acusar falso positivo, adicione uma exceção para este executável.")
    init_database()
    processes.append(run_dash())
    processes.append(run_admin_api())
    print("Painel Dash: http://localhost:8050")
    print("Painel Admin: http://localhost:5000")
    try:
        input("Pressione Enter para encerrar...")
    finally:
        for p in processes:
            p.terminate()
        print("Surebets System finalizado.")
