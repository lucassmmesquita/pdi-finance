"""
PDI Finance - Project Schemas
Schemas Pydantic para validação de dados de projetos
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal


# ==========================================
# PROJETO EXECUTORA SCHEMAS
# ==========================================

class ProjetoExecutoraBase(BaseModel):
    """Schema base de projeto-executora"""
    executora_id: int
    papel: str = Field(default="Executora Principal")
    percentual_participacao: Optional[Decimal] = Field(default=0, ge=0, le=100)
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    
    @validator('papel')
    def validate_papel(cls, v):
        allowed_papeis = ['Executora Principal', 'Co-executora', 'Parceira', 'Colaboradora']
        if v not in allowed_papeis:
            raise ValueError(f'Papel deve ser um de: {", ".join(allowed_papeis)}')
        return v


class ProjetoExecutoraCreate(ProjetoExecutoraBase):
    """Schema para vincular executora a projeto"""
    pass


class ProjetoExecutoraResponse(ProjetoExecutoraBase):
    """Schema de resposta de projeto-executora"""
    id: int
    projeto_id: int
    ativo: bool
    created_at: datetime
    executora_nome: Optional[str] = None
    executora_sigla: Optional[str] = None
    
    class Config:
        from_attributes = True


# ==========================================
# PROJETO SCHEMAS
# ==========================================

class ProjetoBase(BaseModel):
    """Schema base de projeto"""
    codigo: str = Field(..., min_length=3, max_length=50)
    nome: str = Field(..., min_length=5, max_length=200)
    sigla: str = Field(..., min_length=2, max_length=50)
    descricao: Optional[str] = None
    empresa_id: int
    coordenador_id: Optional[int] = None
    tipo: str = Field(..., description="CATI ou CAPDA")
    area_conhecimento: Optional[str] = Field(None, max_length=100)
    data_inicio: date
    data_termino: date
    valor_total: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2)
    numero_parcelas: int = Field(..., gt=0)
    agencia_financiadora: Optional[str] = Field(None, max_length=100)
    numero_contrato: Optional[str] = Field(None, max_length=100)
    observacoes: Optional[str] = None
    
    @validator('tipo')
    def validate_tipo(cls, v):
        if v not in ['CATI', 'CAPDA']:
            raise ValueError('Tipo deve ser CATI ou CAPDA')
        return v
    
    @validator('data_termino')
    def validate_datas(cls, v, values):
        if 'data_inicio' in values and v <= values['data_inicio']:
            raise ValueError('Data de término deve ser posterior à data de início')
        return v


class ProjetoCreate(ProjetoBase):
    """Schema para criação de projeto"""
    executoras: Optional[List[ProjetoExecutoraCreate]] = []


class ProjetoUpdate(BaseModel):
    """Schema para atualização de projeto"""
    codigo: Optional[str] = Field(None, min_length=3, max_length=50)
    nome: Optional[str] = Field(None, min_length=5, max_length=200)
    sigla: Optional[str] = Field(None, min_length=2, max_length=50)
    descricao: Optional[str] = None
    empresa_id: Optional[int] = None
    coordenador_id: Optional[int] = None
    tipo: Optional[str] = None
    area_conhecimento: Optional[str] = None
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    valor_total: Optional[Decimal] = None
    valor_executado: Optional[Decimal] = None
    numero_parcelas: Optional[int] = None
    status: Optional[str] = None
    percentual_execucao: Optional[Decimal] = None
    agencia_financiadora: Optional[str] = None
    numero_contrato: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_status = ['Planejamento', 'Em Execução', 'Concluído', 'Cancelado', 'Suspenso']
            if v not in allowed_status:
                raise ValueError(f'Status deve ser um de: {", ".join(allowed_status)}')
        return v


class ProjetoResponse(ProjetoBase):
    """Schema de resposta de projeto"""
    id: int
    uuid: UUID
    duracao_meses: int
    valor_executado: Decimal
    moeda: str
    status: str
    percentual_execucao: Decimal
    ativo: bool
    created_at: datetime
    updated_at: datetime
    
    # Dados relacionados
    empresa_nome: Optional[str] = None
    empresa_sigla: Optional[str] = None
    coordenador_nome: Optional[str] = None
    numero_executoras: Optional[int] = 0
    
    # Campos calculados
    saldo_disponivel: Optional[Decimal] = None
    percentual_tempo_decorrido: Optional[float] = None
    status_execucao: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProjetoDetalhado(ProjetoResponse):
    """Schema de projeto com detalhes completos"""
    executoras: List[ProjetoExecutoraResponse] = []
    
    class Config:
        from_attributes = True


class ProjetoListResponse(BaseModel):
    """Schema para lista paginada de projetos"""
    total: int
    page: int
    page_size: int
    items: List[ProjetoResponse]