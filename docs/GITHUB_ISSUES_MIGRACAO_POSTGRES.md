# Issues para migração total para PostgreSQL

## Issues Abertas (PENDENTES)

### 1. Refatorar Placeholders de Parâmetro
- Trocar todos os `?` por `%s` nas queries SQL dos testes e fixtures para compatibilidade com PostgreSQL.

### 2. Refatorar Booleans em SQL
- Trocar todos os usos de `is_active = 1`/`is_active = 0` para `is_active = TRUE`/`is_active = FALSE` nas queries SQL dos testes.

### 3. Ajustar Exceções de Banco
- Substituir `sqlite3.IntegrityError` e similares por exceções do PostgreSQL (`psycopg2.IntegrityError` ou equivalente).

### 4. Remover/Adaptar PRAGMA e SQLite-specific
- Remover ou adaptar testes que usam `PRAGMA foreign_keys` ou comandos exclusivos do SQLite.

### 5. Adicionar Views e Triggers Faltantes
- Garantir que as views e triggers requeridas pelos testes (`v_active_opportunities`, `v_user_stats`, etc.) estejam presentes no `schema_postgres.sql`.

### 6. Ajustar Batch Inserts/Updates
- Refatorar todos os batch inserts/updates para usar `%s` e garantir dados no formato correto para PostgreSQL.

### 7. Ajustar Dados de Teste
- Garantir que os dados em `populate.sql` estejam consistentes com os IDs e registros esperados nos testes.

### 8. Remover Mocks/Imports Obsoletos
- Remover patches/mocks de `DatabaseManager` que não existem mais.

### 9. Ajustar/Remover Testes SQLite-only
- Refatorar ou pular testes que dependem de comportamentos exclusivos do SQLite.

---

## Issues Fechadas (RESOLVIDAS em 08/06/2025)

### 1. Remover suporte ao SQLite do backend
- O código agora utiliza apenas PostgreSQL, sem lógica de factory para SQLite.

### 2. Corrigir imports para PostgresDatabaseManager
- Todos os imports relevantes nos testes e no admin_api.py já usam o gerenciador correto.

### 3. Atualizar schema para PostgreSQL
- O arquivo `schema_postgres.sql` foi criado e está em UTF-8, com a coluna `role` adicionada à tabela `users`.

### 4. Atualizar fixture de execução do populate.sql
- O fixture em `conftest.py` executa cada statement separadamente, evitando queries vazias.

### 5. Ajustar inicialização do banco
- O método `_initialize_database` já acessa o resultado de `to_regclass` por nome de coluna.

### 6. Configurar variável de ambiente para testes
- O ambiente de testes já utiliza a variável `POSTGRES_DATABASE_URL` corretamente.

### 7. Mapear padrões problemáticos nos testes
- Todos os padrões problemáticos (booleans, placeholders, views, triggers, SQLite-specific, mocks, dados esperados) já foram identificados e mapeados.

---

> Atualizado em 08/06/2025.
