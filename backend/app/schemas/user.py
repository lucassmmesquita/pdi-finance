"""
PDI Finance - User Schemas
Schemas Pydantic para validação de dados de usuários
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID


# ==========================================
# USER SCHEMAS
# ==========================================

class UserBase(BaseModel):
    """Schema base de usuário (campos comuns)"""
    email: EmailStr
    nome: str = Field(..., min_length=3, max_length=200)
    perfil: str = Field(..., description="Admin, Gestor, Coordenador ou Consulta")
    
    @validator('perfil')
    def validate_perfil(cls, v):
        allowed_perfis = ['Admin', 'Gestor', 'Coordenador', 'Consulta']
        if v not in allowed_perfis:
            raise ValueError(f'Perfil deve ser um de: {", ".join(allowed_perfis)}')
        return v


class UserCreate(UserBase):
    """Schema para criação de usuário"""
    senha: str = Field(..., min_length=8, max_length=100)
    
    @validator('senha')
    def validate_senha(cls, v):
        # Validação básica (validação completa em security.py)
        if len(v) < 8:
            raise ValueError('Senha deve ter no mínimo 8 caracteres')
        return v


class UserUpdate(BaseModel):
    """Schema para atualização de usuário"""
    nome: Optional[str] = Field(None, min_length=3, max_length=200)
    email: Optional[EmailStr] = None
    perfil: Optional[str] = None
    ativo: Optional[bool] = None
    senha: Optional[str] = Field(None, min_length=8, max_length=100)
    
    @validator('perfil')
    def validate_perfil(cls, v):
        if v is not None:
            allowed_perfis = ['Admin', 'Gestor', 'Coordenador', 'Consulta']
            if v not in allowed_perfis:
                raise ValueError(f'Perfil deve ser um de: {", ".join(allowed_perfis)}')
        return v


class UserInDB(UserBase):
    """Schema de usuário completo (do banco de dados)"""
    id: int
    uuid: UUID
    ativo: bool
    ultimo_login: Optional[datetime] = None
    tentativas_login: int = 0
    bloqueado_ate: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Schema de resposta de usuário (dados públicos)"""
    id: int
    uuid: UUID
    nome: str
    email: EmailStr
    perfil: str
    ativo: bool
    ultimo_login: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True


class UserProfile(UserResponse):
    """Schema de perfil do usuário (dados estendidos)"""
    tentativas_login: int = 0
    bloqueado_ate: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True


# ==========================================
# PASSWORD SCHEMAS
# ==========================================

class PasswordChange(BaseModel):
    """Schema para alteração de senha"""
    senha_atual: str = Field(..., min_length=8)
    senha_nova: str = Field(..., min_length=8)
    senha_confirmacao: str = Field(..., min_length=8)
    
    @validator('senha_confirmacao')
    def passwords_match(cls, v, values):
        if 'senha_nova' in values and v != values['senha_nova']:
            raise ValueError('Senhas não conferem')
        return v


class PasswordReset(BaseModel):
    """Schema para reset de senha"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema para confirmação de reset de senha"""
    token: str
    senha_nova: str = Field(..., min_length=8)
    senha_confirmacao: str = Field(..., min_length=8)
    
    @validator('senha_confirmacao')
    def passwords_match(cls, v, values):
        if 'senha_nova' in values and v != values['senha_nova']:
            raise ValueError('Senhas não conferem')
        return v