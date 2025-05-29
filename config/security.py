import os
from hashlib import sha256

SECRET_KEY = os.getenv("SECRET_KEY", "troque-esta-chave") # Mantido para compatibilidade, mas settings.py é a fonte primária

# Função utilitária para gerar hash seguro
# TODO: Para hashing de senhas de usuário, considere usar algoritmos mais robustos e lentos
# como bcrypt ou scrypt, que são projetados especificamente para dificultar ataques de força bruta.
# Exemplo com bcrypt:
# import bcrypt
# def generate_hash_bcrypt(password: str) -> bytes:
#     salt = bcrypt.gensalt()
#     return bcrypt.hashpw(password.encode(), salt)
# def verify_password_bcrypt(password: str, hashed: bytes) -> bool:
#     return bcrypt.checkpw(password.encode(), hashed)

def generate_hash(data: str) -> str:
    return sha256((data + SECRET_KEY).encode()).hexdigest()
