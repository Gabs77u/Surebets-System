#!/usr/bin/env python3
"""
Script de migração e setup do banco de dados SQLite.
Migra dados do PostgreSQL (se houver) e configura o novo banco SQLite.
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime

# Adicionar o diretório backend ao path
BACKEND_DIR = Path(__file__).parent
DATABASE_DIR = BACKEND_DIR / "database"
sys.path.insert(0, str(BACKEND_DIR))

def setup_sqlite_database():
    """Configura o banco de dados SQLite do zero."""
    print("🔧 Configurando banco de dados SQLite...")
    
    try:
        # Importar e usar DatabaseManager
        from database.database import DatabaseManager
        
        db = DatabaseManager()
        
        # Verificar se o banco já existe
        tables = db.fetch("SELECT name FROM sqlite_master WHERE type='table'")
        if tables:
            print(f"📋 Banco já existe com {len(tables)} tabelas")
            return True
        
        # Executar schema
        schema_file = DATABASE_DIR / "schema.sql"
        if schema_file.exists():
            print("📄 Executando schema.sql...")
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
                # Dividir por declarações (SQLite não suporta múltiplas queries)
                for statement in schema_sql.split(';'):
                    statement = statement.strip()
                    if statement:
                        db.execute(statement)
            print("✅ Schema criado com sucesso")
        
        # Executar população inicial
        populate_file = DATABASE_DIR / "populate.sql"
        if populate_file.exists():
            print("📊 Executando populate.sql...")
            with open(populate_file, 'r', encoding='utf-8') as f:
                populate_sql = f.read()
                for statement in populate_sql.split(';'):
                    statement = statement.strip()
                    if statement:
                        db.execute(statement)
            print("✅ Dados iniciais inseridos com sucesso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar banco SQLite: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_backup_directory():
    """Cria diretório de backup se não existir."""
    backup_dir = DATABASE_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)
    return backup_dir

def backup_existing_database():
    """Faz backup do banco existente se houver."""
    try:
        from database.database import DatabaseManager
        
        db = DatabaseManager()
        backup_dir = create_backup_directory()
        
        # Criar nome do backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"backup_migration_{timestamp}.db"
        
        # Fazer backup
        db.backup(str(backup_file))
        print(f"💾 Backup criado: {backup_file}")
        return str(backup_file)
        
    except Exception as e:
        print(f"⚠️ Não foi possível fazer backup: {e}")
        return None

def migrate_from_postgresql():
    """Tenta migrar dados do PostgreSQL se configurado."""
    print("🔄 Verificando migração do PostgreSQL...")
    
    try:
        # Verificar se há configuração do PostgreSQL
        postgres_url = os.getenv("POSTGRES_URL")
        if not postgres_url:
            print("📝 Nenhuma configuração PostgreSQL encontrada")
            return True
        
        print("⚠️ Configuração PostgreSQL encontrada, mas migração automática não implementada")
        print("💡 Se você tinha dados no PostgreSQL, faça a migração manual:")
        print("   1. Exporte os dados do PostgreSQL")
        print("   2. Adapte os dados para SQLite")
        print("   3. Importe usando o DatabaseManager")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração PostgreSQL: {e}")
        return False

def verify_migration():
    """Verifica se a migração foi bem-sucedida."""
    print("🔍 Verificando migração...")
    
    try:
        from database.database import DatabaseManager
        
        db = DatabaseManager()
          # Verificar tabelas essenciais
        essential_tables = ['bookmakers', 'sports', 'leagues', 'markets', 'events', 'selections', 
                          'arbitrage_opportunities', 'arbitrage_history', 'users', 'bets', 
                          'odds_history', 'system_logs']
        
        existing_tables = {row['name'] for row in db.fetch("SELECT name FROM sqlite_master WHERE type='table'")}
        
        missing_tables = set(essential_tables) - existing_tables
        if missing_tables:
            print(f"❌ Tabelas faltando: {missing_tables}")
            return False
        
        # Verificar se há dados de exemplo
        bookmakers_count = db.fetch_one("SELECT COUNT(*) as count FROM bookmakers")
        if bookmakers_count and bookmakers_count['count'] > 0:
            print(f"✅ {bookmakers_count['count']} bookmakers encontradas")
        
        events_count = db.fetch_one("SELECT COUNT(*) as count FROM events")
        if events_count and events_count['count'] > 0:
            print(f"✅ {events_count['count']} eventos encontrados")
        
        print("✅ Migração verificada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def update_environment():
    """Atualiza configurações de ambiente."""
    print("🔧 Atualizando configurações de ambiente...")
    
    env_file = Path(__file__).parent.parent / ".env"
    
    # Sugerir configurações para .env
    suggested_config = f"""
# Configurações SQLite (geradas em {datetime.now()})
DATABASE_PATH={DATABASE_DIR / 'surebets.db'}
DATABASE_BACKUP_DIR={DATABASE_DIR / 'backups'}
MAX_CONNECTIONS=10
CONNECTION_TIMEOUT=30.0

# Remover configurações PostgreSQL se existirem:
# POSTGRES_URL=...
"""
    
    print("💡 Configurações sugeridas para .env:")
    print(suggested_config)
    
    return True

def main():
    print("🚀 MIGRAÇÃO PARA SQLITE - SUREBETS SYSTEM")
    print("=" * 60)
    
    success = True
    
    # 1. Backup do banco existente
    backup_file = backup_existing_database()
    
    # 2. Tentar migração do PostgreSQL
    if not migrate_from_postgresql():
        success = False
    
    # 3. Configurar SQLite
    if not setup_sqlite_database():
        success = False
    
    # 4. Verificar migração
    if not verify_migration():
        success = False
    
    # 5. Atualizar configurações
    if not update_environment():
        success = False
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO DE MIGRAÇÃO")
    print("=" * 60)
    
    if success:
        print("🎉 Migração concluída com sucesso!")
        print("💡 Próximos passos:")
        print("   1. Execute os testes: python run_tests.py")
        print("   2. Inicie o sistema: python ../src/main.py")
        print("   3. Acesse: http://localhost:8050")
        
        if backup_file:
            print(f"   4. Backup disponível em: {backup_file}")
            
    else:
        print("❌ Migração falhou!")
        print("💡 Verifique os erros acima e tente novamente")
        
        if backup_file:
            print(f"🔄 Restaure o backup se necessário: {backup_file}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
