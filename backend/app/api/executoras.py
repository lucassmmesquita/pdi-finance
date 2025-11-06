"""
API de Empresas Executoras
Gestão de empresas executoras dos projetos PD&I
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from uuid import UUID  # Adiciona UUID

from app.core.dependencies import get_db, get_current_user
from app.schemas.user import UserInDB

# Imports dos modelos - ESTRUTURA REAL IDENTIFICADA
from app.models.executora import Executora
from app.models.projetos import Projeto  # ⚠️ Arquivo se chama project.py (inglês)

# ==========================================
# SCHEMAS (ajustados para estrutura REAL do banco)
# ==========================================

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID

class ExecutoraBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=200)
    sigla: str = Field(..., min_length=2, max_length=50)
    tipo: str = Field(..., max_length=50, description="IREDE, IES, ICT, Outro")
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    email: Optional[str] = Field(None, max_length=200)
    telefone: Optional[str] = Field(None, max_length=20)
    responsavel: Optional[str] = Field(None, max_length=200)

class ExecutoraCreate(ExecutoraBase):
    pass

class ExecutoraUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=200)
    sigla: Optional[str] = Field(None, min_length=2, max_length=50)
    tipo: Optional[str] = Field(None, max_length=50)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    email: Optional[str] = Field(None, max_length=200)
    telefone: Optional[str] = Field(None, max_length=20)
    responsavel: Optional[str] = Field(None, max_length=200)
    ativo: Optional[bool] = None

class ExecutoraResponse(ExecutoraBase):
    id: int
    uuid: UUID
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


@router.get("/sigla/{sigla}", response_model=ExecutoraResponse)
def obter_executora_por_sigla(
    sigla: str,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém executora pela sigla
    
    **Requer autenticação**
    """
    executora = db.query(Executora).filter(
        Executora.sigla.ilike(sigla)
    ).first()
    
    if not executora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Executora com sigla '{sigla}' não encontrada"
        )
    
    return executora


@router.get("/nome/{nome}", response_model=ExecutoraResponse)
def obter_executora_por_nome(
    nome: str,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém executora pelo nome
    
    **Requer autenticação**
    """
    executora = db.query(Executora).filter(
        Executora.nome.ilike(f"%{nome}%")
    ).first()
    
    if not executora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Executora com nome '{nome}' não encontrada"
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
    - Nome único
    - Sigla obrigatória
    - Tipo obrigatório (IREDE, IES, ICT, Outro)
    """
    # Verifica permissão
    if current_user.perfil not in ["Admin", "Gestor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas Admin ou Gestor podem cadastrar executoras"
        )
    
    # Verifica se nome já existe
    existe = db.query(Executora).filter(
        Executora.nome == executora.nome
    ).first()
    
    if existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Executora com nome '{executora.nome}' já cadastrada"
        )
    
    # Cria nova executora
    db_executora = Executora(
        nome=executora.nome,
        sigla=executora.sigla,
        tipo=executora.tipo,
        cidade=executora.cidade,
        estado=executora.estado,
        email=executora.email,
        telefone=executora.telefone,
        responsavel=executora.responsavel,
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
        "nome": executora.nome,
        "sigla": executora.sigla,
        "tipo": executora.tipo,
        "localizacao": f"{executora.cidade}/{executora.estado}" if executora.cidade and executora.estado else None,
        "total_projetos": total_projetos,
        "projetos_por_status": {
            status: qtd for status, qtd in projetos_status
        },
        "valor_total_projetos": float(valor_total),
        "primeiro_projeto": datas.primeiro_projeto.isoformat() if datas.primeiro_projeto else None,
        "ultimo_projeto": datas.ultimo_projeto.isoformat() if datas.ultimo_projeto else None,
        "ativo": executora.ativo
    }