import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

import subprocess
from pathlib import Path

# Caminhos relativos robustos
BASE_DIR = Path(__file__).parent.resolve()
BACKEND_DIR = BASE_DIR.parent / "backend"
DB_SCHEMA = BACKEND_DIR / "database" / "schema.sql"
DB_POPULATE = BACKEND_DIR / "database" / "populate.sql"

# Usando os módulos unificados
DASH_PATH = str(BACKEND_DIR / "apps" / "dashboard.py")
ADMIN_API_PATH = str(BACKEND_DIR / "apps" / "admin_api.py")

processes = []

def init_database():
    """Inicializa o banco de dados SQLite com schema e dados"""
    import sqlite3
    import time
    
    print("Inicializando banco de dados SQLite...")
    
    try:
        # Importa e inicializa o banco usando nossa nova classe
        sys.path.append(str(BACKEND_DIR))
        from backend.database.database import DatabaseManager
        
        db = DatabaseManager()
        
        # Verifica se o banco já existe e tem dados
        result = db.fetch_one("SELECT COUNT(*) as count FROM sqlite_master WHERE type='table'")
        if result and result['count'] > 0:
            print("Banco de dados já existe e está configurado.")
            return
        
        # Executa o schema
        print("Criando estrutura do banco...")
        with open(DB_SCHEMA, "r", encoding="utf-8") as f:
            schema_sql = f.read()
            # SQLite não suporta múltiplas queries em uma execução, então vamos dividir
            for statement in schema_sql.split(';'):
                statement = statement.strip()
                if statement:
                    db.execute(statement)
        
        # Popula com dados iniciais
        if DB_POPULATE.exists():
            print("Populando banco com dados iniciais...")
            with open(DB_POPULATE, "r", encoding="utf-8") as f:
                populate_sql = f.read()
                for statement in populate_sql.split(';'):
                    statement = statement.strip()
                    if statement:
                        db.execute(statement)
        
        print("Banco de dados SQLite inicializado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {e}")
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
    frontend_path = BASE_DIR / "frontend" / "tinker_ui.py"
    env = os.environ.copy()
    return subprocess.Popen([sys.executable, str(frontend_path)], env=env)

if __name__ == "__main__":
    print("Iniciando Surebets System (Versão Unificada)...")
    print("Se o antivírus acusar falso positivo, adicione uma exceção para este executável.")
    init_database()
    processes.append(run_dash())
    processes.append(run_admin_api())
    print("Dashboard Unificado: http://localhost:8050")
    print("Admin API Unificada: http://localhost:5000")

    # Aguarda os serviços responderem
    print("Aguardando backend Dash...")
    if not wait_service_ready("http://localhost:8050", timeout=40):
        print("Dash não respondeu a tempo. Encerrando...")
        for p in processes:
            p.terminate()
        sys.exit(1)
    print("Aguardando backend Admin API...")
    if not wait_service_ready("http://localhost:5000/api/games/live", timeout=40):
        print("Admin API não respondeu a tempo. Encerrando...")
        for p in processes:
            p.terminate()
        sys.exit(1)

    # Inicia o frontend Tkinter
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
        print("Surebets System finalizado.")
