# 🔒 Security Guide - Surebets System

## Visão Geral

O sistema Surebets implementa um modelo de segurança abrangente e em camadas (Defense in Depth), com proteções contra as principais vulnerabilidades web listadas no OWASP Top 10. Este documento detalha todas as medidas de segurança implementadas e as melhores práticas para manter o sistema seguro.

---

## 🛡️ Arquitetura de Segurança Implementada

### Múltiplas Camadas de Proteção

1. **Perímetro (Network Layer)**
   - Rate limiting configurável por IP
   - Headers de segurança obrigatórios
   - CORS restrito para domínios confiáveis

2. **Aplicação (Application Layer)**
   - Validação Pydantic rigorosa em todos os endpoints
   - Sanitização automática de inputs
   - Detecção de padrões de ataque (SQL Injection, XSS)

3. **Autenticação (Auth Layer)**
   - Sistema JWT avançado com blacklist
   - Refresh tokens para renovação segura
   - Sistema de roles e permissões granulares

4. **Dados (Data Layer)**
   - Prepared statements para prevenção de SQL Injection
   - Sanitização antes de persistência
   - Audit trail de modificações sensíveis

---

## 🔐 Sistema de Autenticação JWT Avançado

### Funcionalidades Implementadas

- **Access Tokens**: Curta duração (60 minutos configurável)
- **Refresh Tokens**: Longa duração (30 dias configurável)
- **Token Blacklist**: Redis ou memória para tokens revogados
- **Secure Cookies**: Suporte a cookies HttpOnly para SPAs
- **Role-Based Access Control**: Sistema granular de permissões

### Configuração Segura

```bash
# Configurações JWT obrigatórias
JWT_SECRET_KEY=strong-random-key-256-bits
JWT_ACCESS_TOKEN_EXPIRES_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRES_DAYS=30

# Configurações de ambiente
ENVIRONMENT=production
REDIS_URL=redis://localhost:6379/0
```

### Fluxo de Autenticação Seguro

1. **Login**: Validação rigorosa de credenciais
2. **Token Issuance**: Geração de access + refresh tokens
3. **Authorization**: Verificação de roles e permissões
4. **Token Refresh**: Renovação automática quando necessário
5. **Logout**: Adição do token à blacklist

---

## 🎭 Sistema de Roles e Permissões

### Roles Implementados

```python
ROLE_ADMIN = 'admin'      # Acesso total ao sistema
ROLE_OPERATOR = 'operator'  # Operações e gerenciamento de apostas
ROLE_VIEWER = 'viewer'    # Apenas visualização
```

### Mapeamento de Permissões

| Permissão | Admin | Operator | Viewer |
|-----------|-------|----------|--------|
| `can_manage_users` | ✅ | ❌ | ❌ |
| `can_delete_data` | ✅ | ❌ | ❌ |
| `can_configure_system` | ✅ | ❌ | ❌ |
| `can_manage_odds` | ✅ | ✅ | ❌ |
| `can_place_bets` | ✅ | ✅ | ❌ |
| `can_view_reports` | ✅ | ✅ | ✅ |
| `can_view_dashboard` | ✅ | ✅ | ✅ |

### Implementação de Controle de Acesso

```python
# Decoradores implementados
@admin_required          # Apenas admin
@operator_required       # Admin + operator
@viewer_required         # Todos os usuários autenticados
@permission_required('can_manage_users')  # Baseado em permissão específica
```

---

## 🛡️ Validação e Sanitização de Entrada

### Schemas Pydantic Implementados

#### LoginRequestSchema
```python
class LoginRequestSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_.-]+$')
    password: str = Field(..., min_length=6, max_length=128)
    use_cookie: bool = False

    @validator('username')
    def validate_username(cls, v):
        if detect_sql_injection(v) or detect_xss(v):
            raise ValueError("Conteúdo suspeito detectado")
        return sanitize_text(v)
```

#### UserCreateSchema
```python
class UserCreateSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    email: EmailStr
    role: str = Field(..., regex=r'^(admin|operator|viewer)$')

    @validator('password')
    def validate_password_strength(cls, v):
        # Validação de força da senha implementada
        if not re.search(r'[A-Z]', v) or not re.search(r'[a-z]', v) or not re.search(r'\d', v):
            raise ValueError("Senha deve conter ao menos uma maiúscula, minúscula e número")
        return v
```

#### BetInsertSchema
```python
class BetInsertSchema(BaseModel):
    event: str = Field(..., min_length=3, max_length=200)
    market: str = Field(..., min_length=2, max_length=100)
    selection: str = Field(..., min_length=2, max_length=100)
    odd: float = Field(..., gt=1.0, le=1000.0)
    bookmaker: str = Field(..., min_length=2, max_length=50)

    @validator('*', pre=True)
    def sanitize_fields(cls, v):
        if isinstance(v, str):
            if detect_sql_injection(v) or detect_xss(v):
                raise ValueError("Conteúdo suspeito detectado")
            return sanitize_text(v)
        return v
```

### Funções de Detecção de Ataques

#### Detecção de SQL Injection
```python
def detect_sql_injection(text: str) -> bool:
    """Detecta padrões suspeitos de SQL injection."""
    sql_patterns = [
        r"['\";].*(--)|(;)|(\|)|(\*)",  # Comentários SQL
        r"(union|select|insert|delete|update|drop|create|alter)\s",  # Comandos SQL
        r"(exec|execute|sp_|xp_)\s",  # Stored procedures
        r"(script|javascript|vbscript|onload|onerror)",  # Scripts
    ]
    
    text_lower = text.lower()
    for pattern in sql_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    return False
```

#### Detecção de XSS
```python
def detect_xss(text: str) -> bool:
    """Detecta padrões suspeitos de XSS."""
    xss_patterns = [
        r'<script[^>]*>.*?</script>',  # Tags script
        r'javascript:',  # URLs javascript
        r'on\w+\s*=',  # Event handlers
        r'<\s*iframe',  # iframes
        r'<\s*object',  # objects
        r'<\s*embed',   # embeds
    ]
    
    for pattern in xss_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False
```

### Sanitização Automática

```python
def sanitize_text(text: str) -> str:
    """Sanitiza texto removendo conteúdo perigoso."""
    if not isinstance(text, str):
        return text
    
    # Remove caracteres de controle
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    # Normaliza espaços múltiplos
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Sanitização XSS com bleach
    text = bleach.clean(text, tags=[], attributes={}, strip=True)
    
    # Escape HTML
    text = html.escape(text)
    
    return text
```

---

## 🔒 Proteções CSRF e Headers de Segurança

### Headers de Segurança Implementados

```python
@security_headers()
def security_headers_decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        
        # Headers de segurança obrigatórios
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response
    return decorated_function
```

### Proteção CSRF

- Tokens CSRF obrigatórios em operações sensíveis
- Verificação de origem das requisições
- Validação de Content-Type em APIs

---

## 🚦 Rate Limiting e Proteção contra Abuso

### Configurações de Rate Limiting

```bash
# Variáveis de ambiente
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=20
ENABLE_RATE_LIMITING=true
```

### Implementação

- Limite por IP address
- Diferentes limites por endpoint
- Backoff exponencial para IPs bloqueados
- Whitelist para IPs confiáveis

---

## 🔍 Logging e Monitoramento de Segurança

### Eventos de Segurança Logados

```python
def log_security_event(event_type: str, details: str, ip_address: str = None):
    """Registra eventos de segurança para auditoria."""
    logger.warning(f"SECURITY_EVENT: {event_type} | IP: {ip_address} | Details: {details}")
```

### Tipos de Eventos Monitorados

- **LOGIN_FAILED**: Tentativas de login falharam
- **SQL_INJECTION_ATTEMPT**: Tentativa de SQL injection detectada
- **XSS_ATTEMPT**: Tentativa de XSS detectada
- **RATE_LIMIT_EXCEEDED**: Limite de requisições excedido
- **INVALID_TOKEN**: Uso de token inválido ou expirado
- **PERMISSION_DENIED**: Acesso negado por falta de permissão

### Estrutura de Logs

```json
{
  "timestamp": "2023-06-01T12:00:00Z",
  "level": "WARNING",
  "component": "security",
  "event": "SQL_INJECTION_ATTEMPT",
  "user": "anonymous",
  "ip": "192.168.1.100",
  "endpoint": "/api/auth/login",
  "payload_hash": "sha256:...",
  "details": {
    "pattern_detected": "UNION SELECT",
    "blocked": true
  }
}
```

---

## 🧪 Testes de Segurança Implementados

### Estrutura de Testes de Segurança

```
backend/tests/security/
├── test_security_validation.py     # Proteções básicas
├── test_penetration.py            # Testes de penetração
└── conftest.py                    # Fixtures de segurança
```

### Categorias de Testes

#### 1. Testes de Validação de Entrada
- Tentativas de SQL Injection
- Tentativas de XSS
- Payloads maliciosos diversos
- Validação de schemas Pydantic

#### 2. Testes de Autenticação
- Fluxo completo de login/logout
- Renovação de tokens
- Tentativas de acesso não autorizado
- Bypass de autenticação

#### 3. Testes de Autorização
- Verificação de roles
- Escalação de privilégios
- Acesso a recursos protegidos

#### 4. Testes de Rate Limiting
- Múltiplas requisições por IP
- Simulação de DDoS
- Bypass de rate limiting

### Exemplos de Testes

```python
def test_sql_injection_blocked():
    """Testa se tentativas de SQL injection são bloqueadas."""
    malicious_payloads = [
        "'; DROP TABLE users; --",
        "admin' OR '1'='1",
        "1' UNION SELECT * FROM users--"
    ]
    
    for payload in malicious_payloads:
        response = client.post('/api/auth/login', json={
            'username': payload,
            'password': 'test'
        })
        assert response.status_code == 400
        assert 'suspeito' in response.json['error']

def test_xss_sanitization():
    """Testa se conteúdo XSS é sanitizado."""
    xss_payload = "<script>alert('XSS')</script>Valid Event"
    
    response = client.post('/api/admin/insert-bet', json={
        'event': xss_payload,
        'market': 'Test',
        'selection': 'Test',
        'odd': 2.0,
        'bookmaker': 'test'
    }, headers={'Authorization': f'Bearer {admin_token}'})
    
    assert response.status_code == 200
    # Verificar que o script foi removido mas o texto válido permanece
    assert '<script>' not in response.json['event']
    assert 'Valid Event' in response.json['event']
```

---

## 🏗️ Configuração Segura de Produção

### Variáveis de Ambiente Obrigatórias

```bash
# Segurança JWT
JWT_SECRET_KEY=your-256-bit-secret-key
JWT_ACCESS_TOKEN_EXPIRES_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRES_DAYS=30

# Configurações do ambiente
ENVIRONMENT=production
SECRET_KEY=your-flask-secret-key

# Redis para blacklist
REDIS_URL=redis://localhost:6379/0

# Admin seguro
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=pbkdf2:sha256:150000$...

# Rate limiting
RATE_LIMIT_PER_MINUTE=100
ENABLE_CORS=false

# Database
DATABASE_URL=postgresql://user:pass@localhost/surebets_prod

# Logging
LOG_LEVEL=WARNING
ENABLE_DEBUG=false
```

### Checklist de Deploy Seguro

#### Pré-Deploy
- [ ] Todas as variáveis sensíveis em ambiente
- [ ] Senhas fortes geradas aleatoriamente
- [ ] Certificados SSL válidos
- [ ] Firewall configurado adequadamente
- [ ] Backup automatizado configurado

#### Durante Deploy
- [ ] Deploy com usuário não-root
- [ ] Containers com princípio de menor privilégio
- [ ] Network policies restritivas
- [ ] Health checks configurados
- [ ] Monitoring ativo

#### Pós-Deploy
- [ ] Testes de penetração executados
- [ ] Logs de segurança monitorados
- [ ] Alertas configurados
- [ ] Documentação atualizada
- [ ] Equipe treinada

---

## 🚨 Resposta a Incidentes

### Procedimentos de Resposta

#### 1. Detecção
- Monitoring automático de logs de segurança
- Alertas em tempo real para eventos críticos
- Dashboard de métricas de segurança

#### 2. Contenção
```bash
# Bloqueio de IP suspeito
iptables -A INPUT -s SUSPICIOUS_IP -j DROP

# Revogação de tokens comprometidos
curl -X POST /api/auth/revoke-all/USERNAME \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Reinício de serviços se necessário
docker-compose restart backend
```

#### 3. Investigação
- Análise de logs estruturados
- Correlação de eventos
- Identificação do vetor de ataque

#### 4. Recuperação
- Restauração de backups se necessário
- Patches de segurança aplicados
- Teste de funcionalidades críticas

#### 5. Lições Aprendidas
- Documentação do incidente
- Melhoria dos controles
- Atualização de procedimentos

---

## 🔄 Manutenção Contínua de Segurança

### Monitoramento Regular

#### Logs a Monitorar
- Tentativas de login falharam
- Padrões de ataque detectados
- Uso de tokens expirados
- Acessos não autorizados

#### Métricas de Segurança
- Taxa de sucesso de autenticação
- Número de tokens na blacklist
- Tentativas de SQL injection/XSS por hora
- IPs bloqueados por rate limiting

### Atualizações de Segurança

#### Dependências
```bash
# Verificação de vulnerabilidades
pip-audit
safety check

# Atualização automática de dependências
pip-review --auto
```

#### Análise Estática
```bash
# Verificação de código
bandit -r backend/
semgrep --config=auto backend/
```

### Penetration Testing

#### Testes Automatizados
- OWASP ZAP para análise de vulnerabilidades web
- SQLMap para testes de SQL injection
- Nuclei para varredura de vulnerabilidades

#### Testes Manuais
- Revisão de código por especialistas
- Testes de engenharia social
- Avaliação de configurações

---

## 📋 Checklist de Segurança Completo

### Autenticação e Autorização
- [x] **JWT implementado com blacklist**
- [x] **Refresh tokens funcionais**
- [x] **Sistema de roles granular**
- [x] **Permissões baseadas em função**
- [x] **Logout seguro com revogação**

### Validação de Entrada
- [x] **Schemas Pydantic em todos os endpoints**
- [x] **Detecção de SQL injection**
- [x] **Detecção e sanitização de XSS**
- [x] **Validação de força de senha**
- [x] **Sanitização automática de dados**

### Proteções Web
- [x] **Headers de segurança obrigatórios**
- [x] **Proteção CSRF implementada**
- [x] **CORS configurado restritivamente**
- [x] **Rate limiting ativo**
- [x] **Content-Type validation**

### Monitoramento
- [x] **Logging estruturado de eventos**
- [x] **Métricas de segurança coletadas**
- [x] **Alertas configurados**
- [x] **Health checks implementados**
- [x] **Audit trail funcionando**

### Testes
- [x] **Testes unitários de segurança**
- [x] **Testes de integração completos**
- [x] **Testes de penetração automatizados**
- [x] **Validação de payloads maliciosos**
- [x] **Cobertura de código adequada**

### Infraestrutura
- [x] **Variáveis sensíveis externalizadas**
- [x] **Containers com usuário não-root**
- [x] **Backup automatizado**
- [x] **SSL/TLS configurado**
- [x] **Firewall ativo**

---

## 🔗 Recursos e Referências

### Documentação Relacionada
- **[API Documentation](API.md)**: Endpoints e autenticação
- **[Architecture Guide](ARCHITECTURE.md)**: Arquitetura de segurança
- **[JWT Frontend Integration](JWT_FRONTEND_INTEGRACAO.md)**: Integração segura

### Ferramentas de Segurança
- **OWASP ZAP**: Web application scanner
- **Bandit**: Python security linter
- **Safety**: Python dependency checker
- **Nuclei**: Vulnerability scanner

### Compliance e Standards
- **OWASP Top 10**: Vulnerabilidades web mais críticas
- **NIST Cybersecurity Framework**: Framework de segurança
- **ISO 27001**: Padrão de gestão de segurança da informação

---

## 📞 Contato de Segurança

Para relatar vulnerabilidades de segurança:

- **Email**: gabrielaraujoseven@gmail.com
- **GPG Key**: [Public Key]
- **Responsible Disclosure**: 90 dias para correção

**Não divulgue vulnerabilidades publicamente antes da correção.**
