"""
PDI Finance - Security Utilities
JWT, password hashing, token management
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import secrets
import re

from app.core.config import settings


# Configuração do contexto de hashing (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==========================================
# PASSWORD HASHING
# ==========================================

def hash_password(password: str) -> str:
    """
    Gera hash da senha usando bcrypt
    
    Args:
        password: Senha em texto plano
        
    Returns:
        Hash da senha
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha corresponde ao hash
    
    Args:
        plain_password: Senha em texto plano
        hashed_password: Hash armazenado no banco
        
    Returns:
        True se a senha está correta
    """
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Valida a força da senha conforme políticas de segurança
    
    Args:
        password: Senha a ser validada
        
    Returns:
        (is_valid, error_message)
    """
    errors = []
    
    # Tamanho mínimo
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        errors.append(f"mínimo {settings.PASSWORD_MIN_LENGTH} caracteres")
    
    # Letra maiúscula
    if settings.PASSWORD_REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
        errors.append("pelo menos uma letra maiúscula")
    
    # Letra minúscula
    if settings.PASSWORD_REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
        errors.append("pelo menos uma letra minúscula")
    
    # Dígito
    if settings.PASSWORD_REQUIRE_DIGIT and not re.search(r"\d", password):
        errors.append("pelo menos um número")
    
    # Caractere especial
    if settings.PASSWORD_REQUIRE_SPECIAL and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("pelo menos um caractere especial (!@#$%...)")
    
    if errors:
        return False, f"Senha deve conter: {', '.join(errors)}"
    
    return True, "Senha válida"


# ==========================================
# JWT TOKEN GENERATION
# ==========================================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria token JWT de acesso
    
    Args:
        data: Dados a serem incluídos no token (user_id, email, etc)
        expires_delta: Tempo de expiração customizado
        
    Returns:
        Token JWT encoded
    """
    to_encode = data.copy()
    
    # Definir expiração
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Adicionar claims padrão
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
        "jti": secrets.token_urlsafe(32)  # JWT ID único
    })
    
    # Gerar token
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Cria token JWT de refresh (longa duração)
    
    Args:
        data: Dados a serem incluídos no token
        
    Returns:
        Refresh token JWT encoded
    """
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
        "jti": secrets.token_urlsafe(32)
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodifica e valida token JWT
    
    Args:
        token: Token JWT a ser decodificado
        
    Returns:
        Payload do token
        
    Raises:
        HTTPException: Se token inválido ou expirado
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token_type(payload: Dict[str, Any], expected_type: str) -> bool:
    """
    Verifica se o token é do tipo esperado (access ou refresh)
    
    Args:
        payload: Payload decodificado do token
        expected_type: Tipo esperado ('access' ou 'refresh')
        
    Returns:
        True se tipo correto
    """
    token_type = payload.get("type")
    return token_type == expected_type


# ==========================================
# RESET PASSWORD TOKEN
# ==========================================

def generate_reset_token() -> str:
    """
    Gera token seguro para reset de senha
    
    Returns:
        Token aleatório de 32 bytes (URL-safe)
    """
    return secrets.token_urlsafe(32)


def create_reset_token_expiry() -> datetime:
    """
    Cria data de expiração para token de reset (1 hora)
    
    Returns:
        Datetime de expiração
    """
    return datetime.utcnow() + timedelta(hours=1)


# ==========================================
# UTILITIES
# ==========================================

def generate_salt() -> str:
    """
    Gera salt aleatório para senha
    
    Returns:
        Salt em formato string
    """
    return secrets.token_hex(16)


def mask_email(email: str) -> str:
    """
    Mascara email para logs (segurança)
    Exemplo: lucas@exemplo.com -> l****s@exemplo.com
    
    Args:
        email: Email a ser mascarado
        
    Returns:
        Email mascarado
    """
    if not email or "@" not in email:
        return "***"
    
    username, domain = email.split("@", 1)
    
    if len(username) <= 2:
        return f"***@{domain}"
    
    return f"{username[0]}{'*' * (len(username) - 2)}{username[-1]}@{domain}"
