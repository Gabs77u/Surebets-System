# Corrige o encoding do arquivo schema_postgres.sql para UTF-8
with open('backend/database/schema_postgres.sql', 'rb') as f:
    raw = f.read()
try:
    text = raw.decode('utf-8')
except UnicodeDecodeError:
    text = raw.decode('latin1')
with open('backend/database/schema_postgres.sql', 'w', encoding='utf-8') as f:
    f.write(text)
print('Arquivo corrigido para UTF-8.')
