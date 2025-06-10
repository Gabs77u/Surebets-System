# 🐳 Dockerfile - Sistema de Surebets
# Multi-stage build para otimização de produção

# =============================================================================
# STAGE 1: Base Image
# =============================================================================
FROM python:3.11-slim as base

# Metadados da imagem
LABEL maintainer="Surebets Team <dev@surebets.com>"
LABEL version="2.0.0"
LABEL description="Sistema de Detecção de Arbitragem Esportiva"

# Argumentos de build
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Labels adicionais
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0"

# Variáveis de ambiente para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# =============================================================================
# STAGE 2: Dependencies
# =============================================================================
FROM base as dependencies

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN groupadd -r surebets && useradd -r -g surebets surebets

# Criar diretórios necessários
RUN mkdir -p /app /app/logs /app/data /app/static && \
    chown -R surebets:surebets /app

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivo de requisitos
COPY backend/requirements.txt .

# Instalar dependências Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# =============================================================================
# STAGE 3: Production
# =============================================================================
FROM dependencies as production

# Copiar código da aplicação
COPY --chown=surebets:surebets . .

# Criar estrutura de diretórios
RUN mkdir -p logs data static temp && \
    chmod 755 logs data static temp

# Configurar variáveis de ambiente
ENV FLASK_APP=src/main.py \
    FLASK_ENV=production \
    PYTHONPATH=/app

# Expor portas
EXPOSE 5000 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Mudar para usuário não-root
USER surebets

# Comando padrão
CMD ["python", "src/main.py"]

# =============================================================================
# STAGE 4: Development (opcional)
# =============================================================================
FROM dependencies as development

# Instalar dependências de desenvolvimento
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy \
    pre-commit

# Copiar código da aplicação
COPY --chown=surebets:surebets . .

# Configurar variáveis de ambiente para desenvolvimento
ENV FLASK_APP=src/main.py \
    FLASK_ENV=development \
    FLASK_DEBUG=1 \
    PYTHONPATH=/app

# Mudar para usuário não-root
USER surebets

# Comando para desenvolvimento (com hot reload)
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--reload"]
