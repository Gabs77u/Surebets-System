# 🔒 Security Guide - Surebets System

## Princípios Gerais

- Use sempre variáveis de ambiente para segredos (nunca hardcode)
- Proteja endpoints sensíveis com autenticação JWT
- Implemente rate limiting para evitar abusos
- Use HTTPS em produção (Nginx recomendado)
- Valide e sanitize todas as entradas de usuário
- Mantenha dependências sempre atualizadas

---

## Autenticação e Autorização

- JWT obrigatório para rotas administrativas e dashboard
- Expiração de token configurável
- Roles: admin, operador, visualizador
- Logout invalida o token

---

## Proteção de APIs

- Rate limiting (ex: 100 req/min por IP)
- CORS restrito para domínios confiáveis
- CSRF protection nas rotas sensíveis
- Headers de segurança (CSP, X-Frame-Options, HSTS)

---

## Banco de Dados

- Use SQLite apenas para desenvolvimento/teste
- Em produção, prefira PostgreSQL com backup automático
- Habilite foreign key constraints
- Faça backup regular do banco

---

## Logging e Monitoramento

- Nunca logue dados sensíveis (senhas, tokens)
- Use logging estruturado (JSON)
- Monitore health checks e métricas
- Configure alertas para falhas críticas

---

## Atualizações e Patches

- Atualize dependências regularmente
- Monitore CVEs das bibliotecas usadas
- Use ferramentas de análise estática (Bandit, Safety)

---

## Checklist de Segurança

- [x] JWT implementado
- [x] Rate limiting ativo
- [x] HTTPS configurado
- [x] Variáveis sensíveis fora do código
- [x] Backup automático do banco
