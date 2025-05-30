# 🚀 Deployment Guide - Surebets System

## Introdução

Este guia cobre o processo de deploy do sistema Surebets em ambientes de desenvolvimento, staging e produção, incluindo dicas de configuração, variáveis de ambiente e melhores práticas.

---

## 📦 Pré-requisitos

- Docker 20+
- Docker Compose
- Python 3.9+ (para execuções locais)
- Redis 6+ (produção)
- (Opcional) PostgreSQL 13+ (produção)

---

## 🐳 Deploy com Docker Compose (Recomendado)

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/Gabs77u/Surebets-System.git
   cd Surebets-System
   ```
2. **Configure variáveis de ambiente:**
   - Edite `.env` ou `config/settings.py` conforme necessário.
3. **Suba os serviços:**
   ```bash
   docker-compose -f docker/docker-compose.prod.yml up -d
   ```
4. **Verifique a saúde dos serviços:**
   ```bash
   curl http://localhost:5000/health
   ```
5. **Acesse:**
   - Dashboard: http://localhost:5000
   - Admin API: http://localhost:5001

---

## 🛠️ Deploy Manual (Avançado)

1. **Build da imagem:**
   ```bash
   docker build -t surebets-system .
   ```
2. **Execute o container:**
   ```bash
   docker run -p 5000:5000 -p 5001:5001 surebets-system
   ```

---

## 🌍 Ambientes

- **Development:** Docker Compose padrão, SQLite local
- **Staging:** Docker Compose, variáveis de ambiente específicas, Redis
- **Production:** Docker Compose prod, Redis, backup automático, HTTPS

---

## 🔒 Boas Práticas de Deploy

- Sempre use variáveis de ambiente para segredos
- Configure HTTPS e reverse proxy (Nginx recomendado)
- Habilite logging estruturado
- Realize backups regulares do banco
- Monitore health checks e métricas
- Use pipelines CI/CD para automação

---

## 🧩 Troubleshooting

- Verifique logs com `docker-compose logs -f`
- Cheque variáveis de ambiente e permissões
- Teste endpoints `/health` e `/metrics`
- Consulte a documentação oficial para erros específicos

---

## 📚 Referências

- [Documentação Docker](https://docs.docker.com/)
- [Guia Flask Deploy](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Guia Redis](https://redis.io/docs/)
- [Guia Prometheus](https://prometheus.io/docs/)
