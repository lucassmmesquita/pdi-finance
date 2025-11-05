"""
API de Empresas Executoras
Gestão de empresas executoras dos projetos PD&I
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.dependencies import get_db, get_current_user
from app.schemas.user import UserInDB

# Imports dos modelos - ESTRUTURA CORRETA baseada em dependencies.py
from app.models.executora import Executora
from app.models.projetos import Projeto

# ==========================================
# SCHEMAS (temporários - mover para schemas.py depois)
# ==========================================

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class ExecutoraBase(BaseModel):
    cnpj: str = Field(..., description="CNPJ da empresa (14 dígitos)")
    razao_social: str = Field(..., min_length=3, max_length=200)
    nome_fantasia: Optional[str] = Field(None, max_length=200)
    endereco: Optional[str] = None
    telefone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=200)
    responsavel: Optional[str] = Field(None, max_length=200)
    observacoes: Optional[str] = None

class ExecutoraCreate(ExecutoraBase):
    pass

class ExecutoraUpdate(BaseModel):
    razao_social: Optional[str] = Field(None, min_length=3, max_length=200)
    nome_fantasia: Optional[str] = Field(None, max_length=200)
    endereco: Optional[str] = None
    telefone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=200)
    responsavel: Optional[str] = Field(None, max_length=200)
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None

class ExecutoraResponse(ExecutoraBase):
    id: int
    ativo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Pydantic V2 - usa from_attributes
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# ROUTER
# ==========================================

router = APIRouter(prefix="/executoras", tags=["Executoras"])


@router.get("/", response_model=List[ExecutoraResponse])
def listar_executoras(
    skip: int = 0,
    limit: int = 100,
    ativo: bool = None,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todas as empresas executoras com paginação e filtros
    
    **Requer autenticação**
    
    Parâmetros:
    - skip: Número de registros a pular
    - limit: Número máximo de registros
    - ativo: Filtrar por status ativo/inativo
    """
    query = db.query(Executora)
    
    if ativo is not None:
        query = query.filter(Executora.ativo == ativo)
    
    executoras = query.offset(skip).limit(limit).all()
    
    return executoras


@router.get("/{executora_id}", response_model=ExecutoraResponse)
def obter_executora(
    executora_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém detalhes de uma executora específica
    
    **Requer autenticação**
    """
    executora = db.query(Executora).filter(
        Executora.id == executora_id
    ).first()
    
    if not executora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Executora {executora_id} não encontrada"
        )
    
    return executora


@router.get("/cnpj/{cnpj}", response_model=ExecutoraResponse)
def obter_executora_por_cnpj(
    cnpj: str,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém executora pelo CNPJ
    
    **Requer autenticação**
    """
    # Remove formatação do CNPJ
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
    
    executora = db.query(Executora).filter(
        Executora.cnpj == cnpj_limpo
    ).first()
    
    if not executora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Executora com CNPJ {cnpj} não encontrada"
        )
    
    return executora


@router.post("/", response_model=ExecutoraResponse, status_code=status.HTTP_201_CREATED)
def criar_executora(
    executora: ExecutoraCreate,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cadastra nova empresa executora
    
    **Requer autenticação e perfil: Admin ou Gestor**
    
    Validações:
    - CNPJ único (não pode duplicar)
    - Razão social obrigatória
    - CNPJ válido (14 dígitos)
    """
    # Verifica permissão
    if current_user.perfil not in ["Admin", "Gestor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas Admin ou Gestor podem cadastrar executoras"
        )
    
    # Limpa CNPJ
    cnpj_limpo = ''.join(filter(str.isdigit, executora.cnpj))
    
    # Valida tamanho do CNPJ
    if len(cnpj_limpo) != 14:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ deve ter 14 dígitos"
        )
    
    # Verifica se CNPJ já existe
    existe = db.query(Executora).filter(
        Executora.cnpj == cnpj_limpo
    ).first()
    
    if existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Executora com CNPJ {executora.cnpj} já cadastrada"
        )
    
    # Cria nova executora
    db_executora = Executora(
        cnpj=cnpj_limpo,
        razao_social=executora.razao_social,
        nome_fantasia=executora.nome_fantasia,
        endereco=executora.endereco,
        telefone=executora.telefone,
        email=executora.email,
        responsavel=executora.responsavel,
        observacoes=executora.observacoes,
        ativo=True,
        created_at=datetime.now()
    )
    
    db.add(db_executora)
    db.commit()
    db.refresh(db_executora)
    
    return db_executora


@router.put("/{executora_id}", response_model=ExecutoraResponse)
def atualizar_executora(
    executora_id: int,
    executora: ExecutoraUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza dados de uma executora existente
    
    **Requer autenticação e perfil: Admin ou Gestor**
    
    Observação: CNPJ não pode ser alterado
    """
    # Verifica permissão
    if current_user.perfil not in ["Admin", "Gestor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas Admin ou Gestor podem atualizar executoras"
        )
    
    db_executora = db.query(Executora).filter(
        Executora.id == executora_id
    ).first()
    
    if not db_executora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Executora {executora_id} não encontrada"
        )
    
    # Atualiza campos fornecidos
    update_data = executora.model_dump(exclude_unset=True)
    
    # Remove CNPJ se tentou alterar
    if 'cnpj' in update_data:
        del update_data['cnpj']
    
    for field, value in update_data.items():
        setattr(db_executora, field, value)
    
    db_executora.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_executora)
    
    return db_executora


@router.patch("/{executora_id}/ativar", response_model=ExecutoraResponse)
def ativar_executora(
    executora_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ativa uma executora inativa
    
    **Requer autenticação e perfil: Admin ou Gestor**
    """
    # Verifica permissão
    if current_user.perfil not in ["Admin", "Gestor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas Admin ou Gestor podem ativar executoras"
        )
    
    db_executora = db.query(Executora).filter(
        Executora.id == executora_id
    ).first()
    
    if not db_executora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Executora {executora_id} não encontrada"
        )
    
    db_executora.ativo = True
    db_executora.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_executora)
    
    return db_executora


@router.patch("/{executora_id}/inativar", response_model=ExecutoraResponse)
def inativar_executora(
    executora_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Inativa uma executora
    
    **Requer autenticação e perfil: Admin ou Gestor**
    
    Validação: Não pode inativar se houver projetos ativos vinculados
    """
    # Verifica permissão
    if current_user.perfil not in ["Admin", "Gestor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas Admin ou Gestor podem inativar executoras"
        )
    
    db_executora = db.query(Executora).filter(
        Executora.id == executora_id
    ).first()
    
    if not db_executora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Executora {executora_id} não encontrada"
        )
    
    # Verifica se há projetos ativos
    projetos_ativos = db.query(Projeto).filter(
        Projeto.executora_id == executora_id,
        Projeto.status.in_(['Planejamento', 'Em Execução'])
    ).count()
    
    if projetos_ativos > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível inativar. Existem {projetos_ativos} projeto(s) ativo(s)"
        )
    
    db_executora.ativo = False
    db_executora.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_executora)
    
    return db_executora


@router.delete("/{executora_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_executora(
    executora_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove uma executora do sistema
    
    **Requer autenticação e perfil: Admin**
    
    ATENÇÃO: Operação irreversível!
    Validação: Não pode excluir se houver projetos vinculados
    """
    # Verifica permissão (somente Admin)
    if current_user.perfil != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas Admin pode excluir executoras"
        )
    
    db_executora = db.query(Executora).filter(
        Executora.id == executora_id
    ).first()
    
    if not db_executora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Executora {executora_id} não encontrada"
        )
    
    # Verifica se há projetos vinculados
    total_projetos = db.query(Projeto).filter(
        Projeto.executora_id == executora_id
    ).count()
    
    if total_projetos > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível excluir. Existem {total_projetos} projeto(s) vinculado(s)"
        )
    
    db.delete(db_executora)
    db.commit()
    
    return None


@router.get("/{executora_id}/projetos", response_model=List[dict])
def listar_projetos_executora(
    executora_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos os projetos de uma executora
    
    **Requer autenticação**
    
    Retorna lista simplificada com:
    - ID do projeto
    - Código/sigla
    - Nome
    - Status
    - Valor total
    """
    executora = db.query(Executora).filter(
        Executora.id == executora_id
    ).first()
    
    if not executora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Executora {executora_id} não encontrada"
        )
    
    projetos = db.query(Projeto).filter(
        Projeto.executora_id == executora_id
    ).all()
    
    return [
        {
            "id": p.id,
            "codigo": p.codigo,
            "nome": p.nome,
            "status": p.status,
            "valor_total": float(p.valor_total) if p.valor_total else 0.0,
            "data_inicio": p.data_inicio.isoformat() if p.data_inicio else None,
            "data_termino": p.data_termino.isoformat() if p.data_termino else None
        }
        for p in projetos
    ]


@router.get("/{executora_id}/estatisticas")
def obter_estatisticas_executora(
    executora_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas consolidadas da executora
    
    **Requer autenticação**
    
    Métricas:
    - Total de projetos
    - Projetos por status
    - Valor total gerido
    - Período de atuação
    """
    executora = db.query(Executora).filter(
        Executora.id == executora_id
    ).first()
    
    if not executora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Executora {executora_id} não encontrada"
        )
    
    from sqlalchemy import func
    
    # Total de projetos
    total_projetos = db.query(func.count(Projeto.id)).filter(
        Projeto.executora_id == executora_id
    ).scalar()
    
    # Projetos por status
    projetos_status = db.query(
        Projeto.status,
        func.count(Projeto.id).label('quantidade')
    ).filter(
        Projeto.executora_id == executora_id
    ).group_by(Projeto.status).all()
    
    # Valor total
    valor_total = db.query(func.sum(Projeto.valor_total)).filter(
        Projeto.executora_id == executora_id
    ).scalar() or 0
    
    # Datas
    datas = db.query(
        func.min(Projeto.data_inicio).label('primeiro_projeto'),
        func.max(Projeto.data_termino).label('ultimo_projeto')
    ).filter(
        Projeto.executora_id == executora_id
    ).first()
    
    return {
        "executora_id": executora_id,
        "razao_social": executora.razao_social,
        "total_projetos": total_projetos,
        "projetos_por_status": {
            status: qtd for status, qtd in projetos_status
        },
        "valor_total_projetos": float(valor_total),
        "primeiro_projeto": datas.primeiro_projeto.isoformat() if datas.primeiro_projeto else None,
        "ultimo_projeto": datas.ultimo_projeto.isoformat() if datas.ultimo_projeto else None,
        "ativo": executora.ativo
    }