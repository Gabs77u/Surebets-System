# 🚀 Deployment Guide - Surebets System v3.0.0 Security Enterprise

## Introdução

Este guia cobre o processo de deploy do sistema Surebets em ambientes de desenvolvimento, staging e produção, incluindo dicas de configuração, variáveis de ambiente e melhores práticas.

---

## 🔒 Segurança em Produção - v3.0.0

**IMPORTANTE**: Esta versão implementa segurança de nível enterprise. Todos os deploys devem seguir as práticas de segurança documentadas.

---

## 📦 Pré-requisitos

### Básicos
- Docker 20+
- Docker Compose 2.0+
- Python 3.9+ (para execuções locais)
- Redis 6+ (OBRIGATÓRIO para blacklist JWT em produção)

### Produção
- PostgreSQL 13+ (recomendado vs SQLite)
- Nginx como reverse proxy
- Certificados SSL válidos
- Firewall configurado

---

## 🔐 Configuração de Segurança (v3.0.0)

### 1. Variáveis de Ambiente Obrigatórias

```bash
# Segurança JWT
JWT_SECRET_KEY=your-super-secure-256-bit-key
JWT_REFRESH_SECRET_KEY=your-different-refresh-key
JWT_ACCESS_TOKEN_EXPIRES=15  # minutos
JWT_REFRESH_TOKEN_EXPIRES=30  # dias

# Redis para blacklist
REDIS_URL=redis://localhost:6379/0
USE_REDIS_BLACKLIST=true

# Segurança geral
SECURITY_HEADERS_ENABLED=true
RATE_LIMITING_ENABLED=true
SANITIZATION_ENABLED=true

# Ambiente
FLASK_ENV=production
DEBUG=false
```

### 2. Geração de Chaves Seguras

```bash
# Gerar chaves JWT seguras
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_REFRESH_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

---

## 🐳 Deploy com Docker Compose (Recomendado)

### Deploy Desenvolvimento
```bash
git clone https://github.com/Gabs77u/Surebets-System.git
cd Surebets-System
cp .env.example .env  # Configure as variáveis
docker-compose up -d
```

### Deploy Produção Seguro
```bash
# 1. Configure variáveis de produção
cp .env.production.example .env.production
# Edite .env.production com suas chaves

# 2. Deploy com configurações de segurança
docker-compose -f docker/docker-compose.prod.yml up -d

# 3. Verifique segurança
curl -H "X-Real-IP: 1.1.1.1" http://localhost:5000/health
curl -I http://localhost:5000  # Verificar headers de segurança
```

### Verificação de Segurança Pós-Deploy

```bash
# Teste de health com informações de segurança
curl http://localhost:5000/health

# Verificar headers OWASP
curl -I http://localhost:5000/api/auth/login

# Teste rate limiting
for i in {1..20}; do curl http://localhost:5000/api/auth/login; done

# Verificar Redis blacklist
redis-cli ping  # Deve retornar PONG
```

---

## 🛡️ Configuração Nginx para Produção

### nginx.conf (Exemplo)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL/TLS
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    # Headers de segurança adicionais
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;
    limit_req_zone $binary_remote_addr zone=api:10m rate=20r/s;
    
    location /api/auth/ {
        limit_req zone=auth burst=5 nodelay;
        proxy_pass http://localhost:5000;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location / {
        limit_req zone=api burst=10 nodelay;
        proxy_pass http://localhost:5000;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## 🌍 Ambientes e Configurações

### Development
- SQLite local
- JWT em memória (fallback)
- Headers de segurança habilitados
- Rate limiting relaxado
- Debug ativo

### Staging
- Redis obrigatório
- PostgreSQL recomendado
- HTTPS obrigatório
- Rate limiting produção
- Logs estruturados

### Production
- Redis + PostgreSQL obrigatórios
- HTTPS + certificados válidos
- Firewall configurado
- Backup automático
- Monitoramento ativo
- Zero debug/verbose logging

---

## 🔒 Checklist de Segurança Pré-Deploy

### ✅ Autenticação
- [ ] Chaves JWT geradas com `secrets.token_urlsafe(32)`
- [ ] Redis configurado e acessível
- [ ] Expiração de tokens configurada (15min/30dias)
- [ ] Blacklist de tokens funcionando

### ✅ Headers e Proteções
- [ ] `SECURITY_HEADERS_ENABLED=true`
- [ ] CSP, HSTS, X-Frame-Options ativos
- [ ] Rate limiting configurado por ambiente
- [ ] Sanitização automática ativa

### ✅ Infraestrutura
- [ ] HTTPS configurado com certificados válidos
- [ ] Nginx/reverse proxy configurado
- [ ] Firewall bloqueando portas desnecessárias
- [ ] Redis isolado e protegido

### ✅ Monitoramento
- [ ] Endpoint `/health` respondendo
- [ ] Logs estruturados configurados
- [ ] Audit trail de segurança ativo
- [ ] Alertas para tentativas de ataque

---

## 🛠️ Deploy Manual (Avançado)

### Build Seguro
```bash
# Build da imagem com validações
docker build --no-cache -t surebets-system:v3.0.0 .

# Verificar vulnerabilidades
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  -v $PWD:/src aquasec/trivy image surebets-system:v3.0.0
```

### Execução Segura
```bash
# Execute com variáveis de ambiente seguras
docker run -d \
  --name surebets-prod \
  --restart unless-stopped \
  --env-file .env.production \
  -p 127.0.0.1:5000:5000 \
  -p 127.0.0.1:5001:5001 \
  surebets-system:v3.0.0
```

---

## 🚨 Troubleshooting de Segurança

### Problemas Comuns

**JWT não funciona:**
```bash
# Verificar Redis
redis-cli ping
redis-cli keys "blacklist:*"

# Verificar chaves
echo $JWT_SECRET_KEY | wc -c  # Deve ter >32 chars
```

**Rate limiting muito restritivo:**
```bash
# Verificar logs
docker-compose logs -f app | grep "rate limit"

# Ajustar limites temporariamente
# Editar config/settings.py RATE_LIMIT_*
```

**Headers de segurança não aparecem:**
```bash
# Verificar configuração
curl -I http://localhost:5000/health | grep -E "(X-Frame|X-Content|Strict-Transport)"

# Verificar variável
echo $SECURITY_HEADERS_ENABLED
```

### Logs de Segurança
```bash
# Verificar eventos de segurança
docker-compose logs -f app | grep "SECURITY"

# Audit trail
docker-compose logs -f app | grep "AUTH"

# Tentativas de ataque
docker-compose logs -f app | grep -E "(INJECTION|XSS|RATE_LIMIT)"
```

---

## 📊 Monitoramento Pós-Deploy

### Health Checks
```bash
# Health básico
curl http://localhost:5000/health

# Health com autenticação
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/health

# Métricas de segurança
curl http://localhost:5000/metrics | grep -E "(auth|security|rate)"
```

### Validação Contínua
```bash
# Script de validação diária
#!/bin/bash
echo "Validando segurança do sistema..."

# 1. Verificar Redis
redis-cli ping || echo "❌ Redis offline"

# 2. Testar autenticação
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/auth/login || echo "❌ Auth endpoint down"

# 3. Verificar rate limiting
for i in {1..10}; do
  response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/auth/login)
  if [ "$response" == "429" ]; then
    echo "✅ Rate limiting ativo"
    break
  fi
done

echo "Validação concluída"
```

---

## 🎯 Próximos Passos (Roadmap)

### Fase 4: Observabilidade (2 semanas)
- [ ] ELK Stack completo
- [ ] Dashboards Grafana de segurança
- [ ] Alertas automáticos

### Fase 5: Performance (1.5 semanas)
- [ ] Cache distribuído Redis
- [ ] Otimizações de query
- [ ] CDN para assets

### Fase 6: DevOps (2 semanas)
- [ ] Pipeline CI/CD com testes de segurança
- [ ] Deploy automatizado blue/green
- [ ] Rollback automático

---

**Versão**: 3.0.0 - Security Enterprise Release  
**Status**: 🟢 **SECURITY-READY** - Pronto para produção  
**Última atualização**: 22 de dezembro de 2024
