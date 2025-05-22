import os
from hashlib import sha256

SECRET_KEY = os.getenv("SECRET_KEY", "troque-esta-chave")

# Função utilitária para gerar hash seguro

def generate_hash(data: str) -> str:
    return sha256((data + SECRET_KEY).encode()).hexdigest()
