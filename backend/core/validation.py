"""
Módulo de validação e sanitização rigorosa para o sistema Surebets.
Implementa validação de entrada usando Pydantic e sanitização contra XSS/SQL Injection.
"""

from typing import Dict, Any, Optional, List
import re
import html
import bleach
import logging
from pydantic import BaseModel, validator, EmailStr, Field, ValidationError
from marshmallow import Schema, fields, validate
from functools import wraps
from flask import request, jsonify

logger = logging.getLogger(__name__)

# Configurações de sanitização
ALLOWED_TAGS = ["b", "i", "u", "em", "strong", "p", "br"]
ALLOWED_ATTRIBUTES = {}


class SecurityError(Exception):
    """Exceção para violações de segurança."""


class ValidationError(Exception):
    """Exceção para erros de validação."""


# ============= SCHEMAS PYDANTIC =============


class LoginRequestSchema(BaseModel):
    """Schema para validação de login."""

    username: str = Field(
        ..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$"
    )
    password: str = Field(..., min_length=6, max_length=128)
    use_cookie: Optional[bool] = False

    @validator("username")
    def validate_username(cls, v):
        # Verificar caracteres perigosos
        if any(char in v for char in ["<", ">", '"', "'", "&", ";", "(", ")", "|"]):
            raise ValueError("Username contém caracteres não permitidos")
        return v.lower().strip()

    @validator("password")
    def validate_password(cls, v):
        # Verificar tentativas de SQL injection básicas
        sql_patterns = [
            "union",
            "select",
            "drop",
            "delete",
            "insert",
            "update",
            "--",
            ";",
        ]
        v_lower = v.lower()
        if any(pattern in v_lower for pattern in sql_patterns):
            raise ValueError("Password contém padrões suspeitos")
        return v


class UserCreateSchema(BaseModel):
    """Schema para criação de usuário."""

    username: str = Field(
        ..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$"
    )
    password: str = Field(..., min_length=8, max_length=128)
    email: EmailStr
    role: str = Field(..., pattern=r"^(admin|operator|viewer)$")

    @validator("username")
    def validate_username(cls, v):
        sanitized = sanitize_text(v)
        if sanitized != v:
            raise ValueError("Username contém caracteres perigosos")
        return sanitized.lower().strip()

    @validator("password")
    def validate_password_strength(cls, v):
        # Verificar força da senha
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password deve conter pelo menos uma letra maiúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password deve conter pelo menos uma letra minúscula")
        if not re.search(r"\d", v):
            raise ValueError("Password deve conter pelo menos um número")
        return v


class BetInsertSchema(BaseModel):
    """Schema para inserção de apostas."""

    event: str = Field(..., min_length=3, max_length=200)
    market: str = Field(..., min_length=2, max_length=100)
    selection: str = Field(..., min_length=2, max_length=100)
    odd: float = Field(..., gt=1.0, le=1000.0)
    bookmaker: str = Field(..., min_length=2, max_length=50)

    @validator("event", "market", "selection", "bookmaker")
    def sanitize_text_fields(cls, v):
        return sanitize_text(v)

    @validator("odd")
    def validate_odd(cls, v):
        if v <= 1.0:
            raise ValueError("Odd deve ser maior que 1.0")
        if v > 1000.0:
            raise ValueError("Odd não pode ser maior que 1000.0")
        return round(v, 2)


class SearchParamsSchema(BaseModel):
    """Schema para parâmetros de busca."""

    query: Optional[str] = Field(None, max_length=100)
    page: Optional[int] = Field(1, ge=1, le=1000)
    limit: Optional[int] = Field(20, ge=1, le=100)
    sport: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9_-]+$")
    bookmaker: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9_-]+$")

    @validator("query")
    def sanitize_query(cls, v):
        if v:
            return sanitize_text(v)
        return v


# ============= SCHEMAS MARSHMALLOW (ALTERNATIVA) =============


class UserMarshmallowSchema(Schema):
    """Schema Marshmallow para usuários."""

    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))
    role = fields.Str(
        required=True, validate=validate.OneOf(["admin", "operator", "viewer"])
    )


# ============= FUNÇÕES DE SANITIZAÇÃO =============


def sanitize_text(text: str) -> str:
    """
    Sanitiza texto contra XSS, SQLi, Unicode invisível e outros ataques, sem bloquear dados legítimos de scraping.
    """
    if not isinstance(text, str):
        return str(text)

    # Remover caracteres de controle e invisíveis (inclui zero-width, RLO, etc)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f\u200b\u200c\u200d\u202a-\u202e\ufeff]", "", text)

    # Remover múltiplos espaços
    text = re.sub(r"\s+", " ", text).strip()

    # Usar bleach para sanitização XSS (sem tags, sem atributos)
    text = bleach.clean(text, tags=[], attributes={}, strip=True)

    # Remover palavras-chave perigosas (alert, javascript, etc)
    dangerous_keywords = [
        r"alert", r"javascript", r"onerror", r"onload", r"<script>", r"</script>", r"drop table", r"insert into", r"delete from", r"update set"
    ]
    for kw in dangerous_keywords:
        text = re.sub(kw, "", text, flags=re.IGNORECASE)

    # Escape HTML (apenas após bleach e filtro de palavras)
    text = html.escape(text, quote=True)
    # Corrigir duplo escape: substituir '&amp;lt;' por '&lt;' etc
    text = text.replace('&amp;lt;', '&lt;').replace('&amp;gt;', '&gt;').replace('&amp;quot;', '&quot;').replace('&amp;#x27;', '&#x27;').replace('&amp;amp;', '&amp;')

    return text


def detect_sql_injection(text: str) -> bool:
    """
    Detecta tentativas de SQL injection, incluindo variantes clássicas, booleanas, comentários e subqueries.
    """
    if not isinstance(text, str):
        return False
    sql_patterns = [
        r"(;\s*--)",
        r"(;\s*\/\*)",
        r"(\/\*.*\*\/)",  # Comentários /* ... */
        r"(\bunion\b.*\bselect\b)",
        r"(\bdrop\b.*\btable\b)",
        r"(\binsert\b.*\binto\b)",
        r"(\bdelete\b.*\bfrom\b)",
        r"(\bupdate\b.*\bset\b)",
        r"(['\"]?\s*or\s*['\"]?\s*\d+\s*=\s*['\"]?\d+)",  # OR 1=1
        r"(['\"]?\s*and\s*['\"]?\s*\d+\s*=\s*['\"]?\d+)", # AND 1=1
        r"(['\"]\s*or\s*['\"]?1['\"]?=['\"]?1)",
        r"(['\"]\s*and\s*['\"]?1['\"]?=['\"]?1)",
        r"(waitfor\s+delay)",
        r"(sleep\s*\()",
        r"(select\s*\(.*\))",  # subqueries
        r"(ascii\s*\()",
        r"(\b(and|or)\b.*\(\s*select.*\))", # AND (SELECT ...)
        r"(\/\*\*\/|\/\*.*?\*\/)", # /**/ comments
    ]
    text_lower = text.lower()
    for pattern in sql_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            logger.warning(f"Possível SQL injection detectado: {pattern}")
            return True
    return False


def detect_xss(text: str) -> bool:
    """
    Detecta tentativas de XSS, evitando falsos positivos em dados esportivos.
    """
    if not isinstance(text, str):
        return False
    xss_patterns = [
        r"<script.*?>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe.*?>",
        r"<object.*?>",
        r"<embed.*?>",
        r"expression\s*\(",
        r"url\s*\(",
        r"<meta.*?>",
        r"<link.*?>",
    ]
    text_lower = text.lower()
    # Permitir nomes e mercados esportivos comuns
    safe_keywords = [
        "over", "under", "draw", "team", "score", "goals", "match", "winner", "handicap", "corner", "yellow card", "red card"
    ]
    if any(kw in text_lower for kw in safe_keywords):
        return False
    for pattern in xss_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            logger.warning(f"Possível XSS detectado: {pattern}")
            return True
    return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza nomes de arquivo.
    """
    # Remover caracteres perigosos
    filename = re.sub(r'[<>:"/\\|?*]', "", filename)

    # Remover caracteres de controle
    filename = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", filename)

    # Limitar tamanho
    filename = filename[:255]

    return filename.strip()


# ============= DECORADORES DE VALIDAÇÃO =============


def validate_json_schema(schema_class):
    """
    Decorador para validar JSON usando Pydantic e passar validated_data como argumento nomeado para a view.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "JSON payload obrigatório"}), 400

                # Verificar tentativas de ataques antes da validação
                json_str = str(data)
                if detect_sql_injection(json_str):
                    logger.warning(
                        f"Tentativa de SQL injection bloqueada: {request.remote_addr}"
                    )
                    return jsonify({"error": "Conteúdo suspeito detectado"}), 400

                if detect_xss(json_str):
                    logger.warning(f"Tentativa de XSS bloqueada: {request.remote_addr}")
                    return jsonify({"error": "Conteúdo suspeito detectado"}), 400

                # Validar com Pydantic
                validated_data = schema_class(**data)
                kwargs["validated_data"] = validated_data.dict()

            except ValidationError as e:
                logger.warning(f"Erro de validação: {e}")
                return jsonify({"error": "Dados inválidos", "details": str(e)}), 400
            except Exception as e:
                logger.error(f"Erro na validação: {e}")
                return jsonify({"error": "Erro interno de validação"}), 500

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def validate_args_schema(schema_class):
    """
    Decorador para validar argumentos de URL e passar validated_args como argumento nomeado para a view.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Validar argumentos da URL
                validated_args = schema_class(**request.args.to_dict())
                kwargs["validated_args"] = validated_args.dict()
            except ValidationError as e:
                logger.warning(f"Erro de validação de argumentos: {e}")
                return (
                    jsonify({"error": "Parâmetros inválidos", "details": str(e)}),
                    400,
                )
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def security_headers():
    """
    Decorador para adicionar headers de segurança.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)

            # Adicionar headers de segurança
            if hasattr(response, "headers"):
                response.headers["X-Content-Type-Options"] = "nosniff"
                response.headers["X-Frame-Options"] = "DENY"
                response.headers["X-XSS-Protection"] = "1; mode=block"
                response.headers[
                    "Strict-Transport-Security"
                ] = "max-age=31536000; includeSubDomains"
                response.headers[
                    "Content-Security-Policy"
                ] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"

            return response

        return decorated_function

    return decorator


# ============= UTILITÁRIOS =============


def validate_and_sanitize_dict(
    data: Dict[str, Any], allowed_keys: List[str]
) -> Dict[str, Any]:
    """
    Valida e sanitiza um dicionário de dados.
    """
    result = {}

    for key, value in data.items():
        if key not in allowed_keys:
            continue

        if isinstance(value, str):
            # Verificar ataques
            if detect_sql_injection(value) or detect_xss(value):
                raise SecurityError(f"Conteúdo suspeito detectado no campo: {key}")

            # Sanitizar
            value = sanitize_text(value)

        result[key] = value

    return result


def log_security_event(event_type: str, details: str, ip_address: Optional[str] = None):
    """
    Registra eventos de segurança.
    """
    ip = ip_address or (request.remote_addr if request else "unknown")
    logger.warning(f"SECURITY EVENT [{event_type}] from {ip}: {details}")
