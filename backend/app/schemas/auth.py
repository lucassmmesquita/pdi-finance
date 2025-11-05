"""
PDI Finance - Authentication Schemas
Schemas Pydantic para autenticação
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ==========================================
# LOGIN SCHEMAS
# ==========================================

class LoginRequest(BaseModel):
    """Schema para requisição de login"""
    email: EmailStr
    senha: str = Field(..., min_length=1)
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "email": "admin@pdifinance.com",
                "senha": "Admin@2025"
            }]
        }
    }


class LoginResponse(BaseModel):
    """Schema para resposta de login bem-sucedido"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Segundos até expiração do access_token
    user: dict
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": 1,
                    "nome": "Administrador do Sistema",
                    "email": "admin@pdifinance.com",
                    "perfil": "Admin"
                }
            }]
        }
    }


class LoginError(BaseModel):
    """Schema para erro de login"""
    detail: str
    tentativas_restantes: Optional[int] = None
    bloqueado_ate: Optional[datetime] = None


# ==========================================
# REFRESH TOKEN SCHEMAS
# ==========================================

class RefreshTokenRequest(BaseModel):
    """Schema para requisição de refresh token"""
    refresh_token: str = Field(..., description="Refresh token recebido no login")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }]
        }
    }


class RefreshTokenResponse(BaseModel):
    """Schema para resposta de refresh token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }]
        }
    }


# ==========================================
# LOGOUT SCHEMAS
# ==========================================

class LogoutResponse(BaseModel):
    """Schema para resposta de logout"""
    message: str
    logged_out_at: datetime
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "message": "Logout realizado com sucesso",
                "logged_out_at": "2025-11-04T10:30:00"
            }]
        }
    }


# ==========================================
# TOKEN VALIDATION SCHEMAS
# ==========================================

class TokenPayload(BaseModel):
    """Schema para payload do token JWT"""
    sub: str  # user_id como string
    email: str
    perfil: str
    type: str  # "access" ou "refresh"
    exp: datetime
    iat: datetime
    jti: str


class TokenValidationResponse(BaseModel):
    """Schema para resposta de validação de token"""
    valid: bool
    user_id: Optional[int] = None
    email: Optional[str] = None
    perfil: Optional[str] = None
    expires_at: Optional[datetime] = None
    message: Optional[str] = None


# ==========================================
# ME (Current User) SCHEMAS
# ==========================================

class CurrentUserResponse(BaseModel):
    """Schema para resposta do endpoint /me"""
    id: int
    uuid: str
    nome: str
    email: EmailStr
    perfil: str
    ativo: bool
    ultimo_login: Optional[datetime]
    created_at: datetime
    permissions: dict
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [{
                "id": 1,
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "nome": "Administrador do Sistema",
                "email": "admin@pdifinance.com",
                "perfil": "Admin",
                "ativo": True,
                "ultimo_login": "2025-11-04T10:00:00",
                "created_at": "2025-11-01T08:00:00",
                "permissions": {
                    "can_manage_users": True,
                    "can_manage_projects": True,
                    "can_import_files": True,
                    "can_export_reports": True
                }
            }]
        }
    }