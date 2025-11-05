"""
PDI Finance - Executora Schemas
Schemas Pydantic para validação de dados de executoras e empresas
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID


# ==========================================
# EXECUTORA SCHEMAS
# ==========================================

class ExecutoraBase(BaseModel):
    """Schema base de executora"""
    nome: str = Field(..., min_length=3, max_length=200)
    sigla: str = Field(..., min_length=2, max_length=50)
    tipo: str = Field(..., description="IREDE, IES, ICT, Outro")
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, min_length=2, max_length=2)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, max_length=20)
    responsavel: Optional[str] = Field(None, max_length=200)
    
    @validator('tipo')
    def validate_tipo(cls, v):
        allowed_tipos = ['IREDE', 'IES', 'ICT', 'Outro']
        if v not in allowed_tipos:
            raise ValueError(f'Tipo deve ser um de: {", ".join(allowed_tipos)}')
        return v
    
    @validator('estado')
    def validate_estado(cls, v):
        if v:
            return v.upper()
        return v


class ExecutoraCreate(ExecutoraBase):
    """Schema para criação de executora"""
    pass


class ExecutoraUpdate(BaseModel):
    """Schema para atualização de executora"""
    nome: Optional[str] = Field(None, min_length=3, max_length=200)
    sigla: Optional[str] = Field(None, min_length=2, max_length=50)
    tipo: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    responsavel: Optional[str] = None
    ativo: Optional[bool] = None


class ExecutoraResponse(ExecutoraBase):
    """Schema de resposta de executora"""
    id: int
    uuid: UUID
    ativo: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==========================================
# EMPRESA SCHEMAS
# ==========================================

class EmpresaBase(BaseModel):
    """Schema base de empresa"""
    nome: str = Field(..., min_length=3, max_length=200)
    sigla: str = Field(..., min_length=2, max_length=50)
    cnpj: Optional[str] = Field(None, max_length=18)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, max_length=20)


class EmpresaCreate(EmpresaBase):
    """Schema para criação de empresa"""
    pass


class EmpresaUpdate(BaseModel):
    """Schema para atualização de empresa"""
    nome: Optional[str] = Field(None, min_length=3, max_length=200)
    sigla: Optional[str] = Field(None, min_length=2, max_length=50)
    cnpj: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    ativo: Optional[bool] = None


class EmpresaResponse(EmpresaBase):
    """Schema de resposta de empresa"""
    id: int
    uuid: UUID
    ativo: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True