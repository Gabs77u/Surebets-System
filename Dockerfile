# Dockerfile para Surebets System
FROM python:3.11-slim

WORKDIR /app

# Copia requirements e instala dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o projeto
COPY . .

# Expõe as portas do Dash e do Admin API
EXPOSE 8050 5000

# Comando para rodar ambos os serviços
CMD ["python", "main.py"]
