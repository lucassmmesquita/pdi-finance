"""
API de Projetos PD&I
Gestão completa de projetos de Pesquisa, Desenvolvimento e Inovação
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

from app.core.dependencies import get_db, get_current_user
from app.schemas.user import UserInDB

# Imports dos modelos - ESTRUTURA CORRETA baseada em dependencies.py
from app.models.projetos import Projeto
from app.models.executora import Executora
#from app.models.inciso import Inciso
#from app.models.rh import RecursoHumano
#from app.models.aporte import Aporte
#from app.models.despesa import Despesa

# Schemas temporários (mover para schemas.py depois)
from pydantic import BaseModel, Field, ConfigDict

class ProjetoBase(BaseModel):
    codigo: str = Field(..., min_length=3, max_length=50)
    nome: str = Field(..., min_length=3, max_length=200)
    descricao: Optional[str] = None
    valor_total: Optional[Decimal] = Field(None, ge=0)
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    status: Optional[str] = Field("Planejamento", pattern="^(Planejamento|Em Execução|Concluído|Cancelado)$")
    coordenador: Optional[str] = Field(None, max_length=200)
    executora_id: int
    agencia_financiadora: Optional[str] = Field(None, max_length=200)
    numero_convenio: Optional[str] = Field(None, max_length=100)
    observacoes: Optional[str] = None

class ProjetoCreate(ProjetoBase):
    pass

class ProjetoUpdate(BaseModel):
    codigo: Optional[str] = Field(None, min_length=3, max_length=50)
    nome: Optional[str] = Field(None, min_length=3, max_length=200)
    descricao: Optional[str] = None
    valor_total: Optional[Decimal] = Field(None, ge=0)
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(Planejamento|Em Execução|Concluído|Cancelado)$")
    coordenador: Optional[str] = Field(None, max_length=200)
    agencia_financiadora: Optional[str] = Field(None, max_length=200)
    numero_convenio: Optional[str] = Field(None, max_length=100)
    observacoes: Optional[str] = None

class ProjetoResponse(ProjetoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Pydantic V2 - usa from_attributes
    model_config = ConfigDict(from_attributes=True)

router = APIRouter(prefix="/projetos", tags=["Projetos"])


@router.get("/", response_model=List[ProjetoResponse])
def listar_projetos(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    executora_id: Optional[int] = None,
    data_inicio_de: Optional[date] = None,
    data_inicio_ate: Optional[date] = None,
    busca: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista projetos com paginação e filtros avançados
    
    **Requer autenticação**
    
    Filtros disponíveis:
    - status: 'Planejamento', 'Em Execução', 'Concluído', 'Cancelado'
    - executora_id: ID da empresa executora
    - data_inicio_de/ate: Período de início
    - busca: Busca por código, nome ou descrição
    """
    query = db.query(Projeto)
    
    # Aplica filtros
    if status:
        query = query.filter(Projeto.status == status)
    
    if executora_id:
        query = query.filter(Projeto.executora_id == executora_id)
    
    if data_inicio_de:
        query = query.filter(Projeto.data_inicio >= data_inicio_de)
    
    if data_inicio_ate:
        query = query.filter(Projeto.data_inicio <= data_inicio_ate)
    
    if busca:
        busca_pattern = f"%{busca}%"
        query = query.filter(
            or_(
                Projeto.codigo.ilike(busca_pattern),
                Projeto.nome.ilike(busca_pattern),
                Projeto.descricao.ilike(busca_pattern)
            )
        )
    
    # Ordena por data de criação (mais recentes primeiro)
    query = query.order_by(Projeto.created_at.desc())
    
    projetos = query.offset(skip).limit(limit).all()
    
    return projetos


@router.get("/{projeto_id}", response_model=dict)
def obter_projeto(
    projeto_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém detalhes completos de um projeto específico
    
    **Requer autenticação**
    
    Inclui:
    - Dados do projeto
    - Informações da executora
    - Estatísticas de incisos
    - Total de RH
    - Total de aportes e despesas
    """
    projeto = db.query(Projeto).filter(Projeto.id == projeto_id).first()
    
    if not projeto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Projeto {projeto_id} não encontrado"
        )
    
    # Calcula estatísticas
    stats = calcular_estatisticas_projeto(projeto_id, db)
    
    return {
        "id": projeto.id,
        "codigo": projeto.codigo,
        "nome": projeto.nome,
        "descricao": projeto.descricao,
        "valor_total": float(projeto.valor_total) if projeto.valor_total else 0.0,
        "data_inicio": projeto.data_inicio.isoformat() if projeto.data_inicio else None,
        "data_termino": projeto.data_termino.isoformat() if projeto.data_termino else None,
        "status": projeto.status,
        "coordenador": projeto.coordenador,
        "executora_id": projeto.executora_id,
        "agencia_financiadora": projeto.agencia_financiadora,
        "numero_convenio": projeto.numero_convenio,
        "observacoes": projeto.observacoes,
        "created_at": projeto.created_at.isoformat(),
        "updated_at": projeto.updated_at.isoformat() if projeto.updated_at else None,
        "estatisticas": stats
    }


@router.get("/codigo/{codigo}", response_model=ProjetoResponse)
def obter_projeto_por_codigo(
    codigo: str,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém projeto pelo código/sigla
    
    **Requer autenticação**
    """
    projeto = db.query(Projeto).filter(Projeto.codigo == codigo).first()
    
    if not projeto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Projeto com código '{codigo}' não encontrado"
        )
    
    return projeto


@router.post("/", response_model=ProjetoResponse, status_code=status.HTTP_201_CREATED)
def criar_projeto(
    projeto: ProjetoCreate,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria novo projeto PD&I
    
    **Requer autenticação e perfil: Admin, Gestor ou Coordenador**
    
    Validações:
    - Código único
    - Executora deve existir
    - Data término > Data início
    - Valor total > 0
    """
    # Verifica permissão
    if current_user.perfil not in ["Admin", "Gestor", "Coordenador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas Admin, Gestor ou Coordenador podem criar projetos"
        )
    
    # Verifica código único
    existe = db.query(Projeto).filter(Projeto.codigo == projeto.codigo).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe projeto com código '{projeto.codigo}'"
        )
    
    # Verifica executora
    executora = db.query(Executora).filter(Executora.id == projeto.executora_id).first()
    if not executora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Executora {projeto.executora_id} não encontrada"
        )
    
    if not executora.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Executora está inativa"
        )
    
    # Valida datas
    if projeto.data_termino and projeto.data_inicio:
        if projeto.data_termino <= projeto.data_inicio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data de término deve ser posterior à data de início"
            )
    
    # Valida valor
    if projeto.valor_total and projeto.valor_total <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valor total deve ser maior que zero"
        )
    
    # Cria projeto
    db_projeto = Projeto(
        codigo=projeto.codigo,
        nome=projeto.nome,
        descricao=projeto.descricao,
        valor_total=projeto.valor_total,
        data_inicio=projeto.data_inicio,
        data_termino=projeto.data_termino,
        status=projeto.status or 'Planejamento',
        coordenador=projeto.coordenador,
        executora_id=projeto.executora_id,
        agencia_financiadora=projeto.agencia_financiadora,
        numero_convenio=projeto.numero_convenio,
        observacoes=projeto.observacoes,
        created_at=datetime.now()
    )
    
    db.add(db_projeto)
    db.commit()
    db.refresh(db_projeto)
    
    # Cria incisos padrão (I a V)
    criar_incisos_padrao(db_projeto.id, db)
    
    return db_projeto


@router.put("/{projeto_id}", response_model=ProjetoResponse)
def atualizar_projeto(
    projeto_id: int,
    projeto: ProjetoUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza dados de um projeto existente
    
    **Requer autenticação e perfil: Admin, Gestor ou Coordenador**
    """
    # Verifica permissão
    if current_user.perfil not in ["Admin", "Gestor", "Coordenador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas Admin, Gestor ou Coordenador podem atualizar projetos"
        )
    
    db_projeto = db.query(Projeto).filter(Projeto.id == projeto_id).first()
    
    if not db_projeto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Projeto {projeto_id} não encontrado"
        )
    
    # Valida código único se alterado
    if projeto.codigo and projeto.codigo != db_projeto.codigo:
        existe = db.query(Projeto).filter(
            Projeto.codigo == projeto.codigo,
            Projeto.id != projeto_id
        ).first()
        if existe:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe outro projeto com código '{projeto.codigo}'"
            )
    
    # Valida datas
    data_inicio = projeto.data_inicio or db_projeto.data_inicio
    data_termino = projeto.data_termino or db_projeto.data_termino
    
    if data_inicio and data_termino and data_termino <= data_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data de término deve ser posterior à data de início"
        )
    
    # Atualiza campos
    update_data = projeto.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_projeto, field, value)
    
    db_projeto.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_projeto)
    
    return db_projeto


@router.patch("/{projeto_id}/status", response_model=ProjetoResponse)
def atualizar_status_projeto(
    projeto_id: int,
    novo_status: str = Query(..., pattern="^(Planejamento|Em Execução|Concluído|Cancelado)$"),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza apenas o status do projeto
    
    **Requer autenticação e perfil: Admin, Gestor ou Coordenador**
    
    Status válidos:
    - Planejamento
    - Em Execução
    - Concluído
    - Cancelado
    """
    # Verifica permissão
    if current_user.perfil not in ["Admin", "Gestor", "Coordenador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para alterar status"
        )
    
    db_projeto = db.query(Projeto).filter(Projeto.id == projeto_id).first()
    
    if not db_projeto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Projeto {projeto_id} não encontrado"
        )
    
    db_projeto.status = novo_status
    db_projeto.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_projeto)
    
    return db_projeto


@router.delete("/{projeto_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_projeto(
    projeto_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove um projeto do sistema
    
    **Requer autenticação e perfil: Admin**
    
    ATENÇÃO: Operação em cascata! Remove:
    - Projeto
    - Incisos vinculados
    - Recursos humanos
    - Aportes
    - Despesas
    - Todos os dados relacionados
    """
    # Verifica permissão (somente Admin)
    if current_user.perfil != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas Admin pode excluir projetos"
        )
    
    db_projeto = db.query(Projeto).filter(Projeto.id == projeto_id).first()
    
    if not db_projeto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Projeto {projeto_id} não encontrado"
        )
    
    # Remove em cascata (configurado no modelo)
    db.delete(db_projeto)
    db.commit()
    
    return None


@router.get("/{projeto_id}/dashboard")
def obter_dashboard_projeto(
    projeto_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna dados consolidados para o dashboard do projeto
    
    **Requer autenticação**
    
    Inclui:
    - KPIs principais
    - Gráficos de evolução
    - Status por inciso
    - Alertas e pendências
    """
    projeto = db.query(Projeto).filter(Projeto.id == projeto_id).first()
    
    if not projeto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Projeto {projeto_id} não encontrado"
        )
    
    # KPIs
    kpis = calcular_kpis_projeto(projeto_id, db)
    
    # Evolução mensal
    evolucao = obter_evolucao_mensal(projeto_id, db)
    
    # Status por inciso
    incisos = obter_status_incisos(projeto_id, db)
    
    # Alertas
    alertas = gerar_alertas_projeto(projeto_id, db)
    
    return {
        "projeto": {
            "id": projeto.id,
            "codigo": projeto.codigo,
            "nome": projeto.nome,
            "status": projeto.status
        },
        "kpis": kpis,
        "evolucao_mensal": evolucao,
        "incisos": incisos,
        "alertas": alertas
    }


# ===== FUNÇÕES AUXILIARES =====

def criar_incisos_padrao(projeto_id: int, db: Session):
    """Cria os 5 incisos padrão para um novo projeto"""
    incisos_padrao = [
        {"codigo": "I", "nome": "Equipamentos, máquinas e softwares", "ordem": 1},
        {"codigo": "II", "nome": "Recursos Humanos", "ordem": 2},
        {"codigo": "III", "nome": "Serviços de terceiros", "ordem": 3},
        {"codigo": "IV", "nome": "Materiais de consumo", "ordem": 4},
        {"codigo": "V", "nome": "Intercâmbio e outros", "ordem": 5}
    ]
    
    for inc in incisos_padrao:
        db_inciso = Inciso(
            projeto_id=projeto_id,
            codigo=inc["codigo"],
            nome=inc["nome"],
            ordem=inc["ordem"],
            valor_previsto=Decimal('0.00'),
            valor_executado=Decimal('0.00')
        )
        db.add(db_inciso)
    
    db.commit()


def calcular_estatisticas_projeto(projeto_id: int, db: Session):
    """Calcula estatísticas gerais do projeto"""
    
    # Total de incisos
    total_incisos = db.query(func.count(Inciso.id)).filter(
        Inciso.projeto_id == projeto_id
    ).scalar()
    
    # Total previsto e executado
    totais_incisos = db.query(
        func.sum(Inciso.valor_previsto).label('previsto'),
        func.sum(Inciso.valor_executado).label('executado')
    ).filter(Inciso.projeto_id == projeto_id).first()
    
    # Recursos humanos
    total_rh = db.query(func.count(RecursoHumano.id)).filter(
        RecursoHumano.projeto_id == projeto_id,
        RecursoHumano.status == 'Ativo'
    ).scalar()
    
    # Aportes
    aportes = db.query(
        func.count(Aporte.id).label('quantidade'),
        func.sum(Aporte.disponivel_execucao).label('total')
    ).filter(Aporte.projeto_id == projeto_id).first()
    
    # Despesas
    despesas = db.query(
        func.count(Despesa.id).label('quantidade'),
        func.sum(Despesa.valor_liquido).label('total')
    ).filter(Despesa.projeto_id == projeto_id).first()
    
    return {
        "total_incisos": total_incisos,
        "valor_previsto": float(totais_incisos.previsto or 0),
        "valor_executado": float(totais_incisos.executado or 0),
        "percentual_execucao": round((float(totais_incisos.executado or 0) / float(totais_incisos.previsto or 1)) * 100, 2),
        "total_rh_ativo": total_rh,
        "total_aportes": aportes.quantidade,
        "valor_aportes": float(aportes.total or 0),
        "total_despesas": despesas.quantidade,
        "valor_despesas": float(despesas.total or 0)
    }


def calcular_kpis_projeto(projeto_id: int, db: Session):
    """Calcula KPIs principais"""
    stats = calcular_estatisticas_projeto(projeto_id, db)
    
    saldo = stats["valor_aportes"] - stats["valor_despesas"]
    
    return {
        "orcamento_total": stats["valor_previsto"],
        "percentual_executado": stats["percentual_execucao"],
        "saldo_disponivel": saldo,
        "total_despesas": stats["valor_despesas"]
    }


def obter_evolucao_mensal(projeto_id: int, db: Session):
    """Retorna evolução mensal de execução (últimos 12 meses)"""
    # Implementação simplificada - expandir conforme necessário
    return []


def obter_status_incisos(projeto_id: int, db: Session):
    """Retorna status de cada inciso"""
    incisos = db.query(Inciso).filter(Inciso.projeto_id == projeto_id).all()
    
    return [
        {
            "codigo": inc.codigo,
            "nome": inc.nome,
            "previsto": float(inc.valor_previsto),
            "executado": float(inc.valor_executado),
            "percentual": round((float(inc.valor_executado) / float(inc.valor_previsto or 1)) * 100, 2)
        }
        for inc in incisos
    ]


def gerar_alertas_projeto(projeto_id: int, db: Session):
    """Gera alertas automáticos baseados em regras de negócio"""
    alertas = []
    stats = calcular_estatisticas_projeto(projeto_id, db)
    
    # Alerta de saldo baixo
    saldo = stats["valor_aportes"] - stats["valor_despesas"]
    if saldo < stats["valor_previsto"] * 0.1:
        alertas.append({
            "tipo": "warning",
            "mensagem": "Saldo disponível abaixo de 10% do orçamento"
        })
    
    # Alerta de execução atrasada
    if stats["percentual_execucao"] < 50:
        alertas.append({
            "tipo": "info",
            "mensagem": "Execução orçamentária abaixo de 50%"
        })
    
    return alertas