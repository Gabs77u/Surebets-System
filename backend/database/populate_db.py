import psycopg2
import os

# Configurações do banco de dados
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'surebets')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'postgres')
DB_PORT = os.getenv('DB_PORT', '5432')

SQL_FILE = os.path.join(os.path.dirname(__file__), 'populate.sql')

def run_populate():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        conn.autocommit = True
        cur = conn.cursor()
        with open(SQL_FILE, 'r', encoding='utf-8') as f:
            sql = f.read()
            cur.execute(sql)
        print('Banco de dados populado com sucesso!')
        cur.close()
        conn.close()
    except Exception as e:
        print(f'Erro ao popular o banco de dados: {e}')

if __name__ == '__main__':
    run_populate()
