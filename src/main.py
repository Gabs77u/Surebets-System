import sys
import os
import subprocess
from pathlib import Path
import logging

# Caminhos relativos robustos
BASE_DIR = Path(__file__).parent.resolve()
BACKEND_DIR = BASE_DIR.parent / "backend"
DB_SCHEMA = BACKEND_DIR / "database" / "schema.sql"
DB_POPULATE = BACKEND_DIR / "database" / "populate.sql"

DASH_PATH = str(BACKEND_DIR / "apps" / "dashboard.py")
ADMIN_API_PATH = str(BACKEND_DIR / "apps" / "admin_api.py")

processes = []

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("surebets_system.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)


def init_database():
    """Inicializa o banco de dados SQLite com schema e dados"""
    import sqlite3
    import time
    logging.info("Inicializando banco de dados SQLite...")
    try:
        backend_path = str(BACKEND_DIR)
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        project_root = str(BASE_DIR.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from backend.database.database import DatabaseManager
        db = DatabaseManager()
        result = db.fetch_one("SELECT COUNT(*) as count FROM sqlite_master WHERE type='table'")
        if result and result['count'] > 0:
            logging.info("Banco de dados já existe e está configurado.")
            return
        logging.info("Criando estrutura do banco...")
        with open(DB_SCHEMA, "r", encoding="utf-8") as f:
            schema_sql = f.read()
            for statement in schema_sql.split(';'):
                statement = statement.strip()
                if statement:
                    db.execute(statement)
        if DB_POPULATE.exists():
            logging.info("Populando banco com dados iniciais...")
            with open(DB_POPULATE, "r", encoding="utf-8") as f:
                populate_sql = f.read()
                for statement in populate_sql.split(';'):
                    statement = statement.strip()
                    if statement:
                        db.execute(statement)
        logging.info("Banco de dados SQLite inicializado com sucesso!")
    except Exception as e:
        logging.error(f"Erro ao inicializar banco de dados: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_dash():
    env = os.environ.copy()
    return subprocess.Popen([sys.executable, DASH_PATH], env=env)


def run_admin_api():
    env = os.environ.copy()
    return subprocess.Popen([sys.executable, ADMIN_API_PATH], env=env)


def wait_service_ready(url, timeout=30):
    import requests
    import time
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(url, timeout=2)
            if resp.status_code == 200:
                return True
        except Exception:
            time.sleep(1)
    return False


def run_tkinter_frontend():
    frontend_path = BASE_DIR.parent / "frontend" / "tinker_ui.py"
    env = os.environ.copy()
    return subprocess.Popen([sys.executable, str(frontend_path)], env=env)


if __name__ == "__main__":
    logging.info("Iniciando Surebets System (Versão Unificada)...")
    logging.info("Se o antivírus acusar falso positivo, adicione uma exceção para este executável.")
    init_database()
    processes.append(run_dash())
    processes.append(run_admin_api())
    logging.info("Dashboard Unificado: http://localhost:8050")
    logging.info("Admin API Unificada: http://localhost:5000")
    logging.info("Aguardando backend Dash...")
    if not wait_service_ready("http://localhost:8050", timeout=40):
        logging.error("Dash não respondeu a tempo. Encerrando...")
        for p in processes:
            p.terminate()
        sys.exit(1)
    logging.info("Aguardando backend Admin API...")
    if not wait_service_ready("http://localhost:5000/api/games/live", timeout=40):
        logging.error("Admin API não respondeu a tempo. Encerrando...")
        for p in processes:
            p.terminate()
        sys.exit(1)
    frontend_proc = run_tkinter_frontend()
    processes.append(frontend_proc)
    try:
        input("Pressione Enter para encerrar...")
    finally:
        for p in processes:
            p.terminate()
            try:
                p.wait(timeout=5)
            except Exception:
                pass
        logging.info("Surebets System finalizado.")
