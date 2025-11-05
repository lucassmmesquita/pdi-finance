"""
PDI Finance - Project Service
Lógica de negócio para projetos
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status
from datetime import date

from backend.app.models.projetos import Projeto, ProjetoExecutora
from app.models.executora import Executora, Empresa
from app.models.user import Usuario
from app.schemas.project import (
    ProjetoCreate, 
    ProjetoUpdate, 
    ProjetoExecutoraCreate,
    ProjetoResponse
)


class ProjetoService:
    """Serviço para gerenciar projetos"""
    
    @staticmethod
    def get_all(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        empresa_id: Optional[int] = None,
        tipo: Optional[str] = None,
        status: Optional[str] = None,
        ativo: Optional[bool] = True
    ) -> tuple[List[Projeto], int]:
        """
        Lista todos os projetos com filtros
        
        Args:
            db: Sessão do banco
            skip: Registros para pular
            limit: Limite de registros
            empresa_id: Filtrar por empresa
            tipo: Filtrar por tipo (CATI/CAPDA)
            status: Filtrar por status
            ativo: Filtrar por ativo
            
        Returns:
            Tuple (lista de projetos, total de registros)
        """
        query = db.query(Projeto)
        
        # Aplicar filtros
        if ativo is not None:
            query = query.filter(Projeto.ativo == ativo)
        
        if empresa_id:
            query = query.filter(Projeto.empresa_id == empresa_id)
        
        if tipo:
            query = query.filter(Projeto.tipo == tipo)
        
        if status:
            query = query.filter(Projeto.status == status)
        
        # Contar total
        total = query.count()
        
        # Aplicar paginação e ordenar
        projetos = query.order_by(Projeto.created_at.desc()).offset(skip).limit(limit).all()
        
        return projetos, total
    
    
    @staticmethod
    def get_by_id(db: Session, projeto_id: int) -> Optional[Projeto]:
        """
        Busca projeto por ID
        
        Args:
            db: Sessão do banco
            projeto_id: ID do projeto
            
        Returns:
            Projeto encontrado ou None
        """
        return db.query(Projeto).filter(Projeto.id == projeto_id).first()
    
    
    @staticmethod
    def get_by_codigo(db: Session, codigo: str) -> Optional[Projeto]:
        """
        Busca projeto por código
        
        Args:
            db: Sessão do banco
            codigo: Código do projeto
            
        Returns:
            Projeto encontrado ou None
        """
        return db.query(Projeto).filter(Projeto.codigo == codigo).first()
    
    
    @staticmethod
    def create(db: Session, projeto_data: ProjetoCreate, user_id: int = None) -> Projeto:
        """
        Cria novo projeto
        
        Args:
            db: Sessão do banco
            projeto_data: Dados do projeto
            user_id: ID do usuário criador
            
        Returns:
            Projeto criado
            
        Raises:
            HTTPException: Se código já existe ou dados inválidos
        """
        # Verificar se código já existe
        existing = ProjetoService.get_by_codigo(db, projeto_data.codigo)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Projeto com código '{projeto_data.codigo}' já existe"
            )
        
        # Verificar se empresa existe
        empresa = db.query(Empresa).filter(Empresa.id == projeto_data.empresa_id).first()
        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Empresa com ID {projeto_data.empresa_id} não encontrada"
            )
        
        # Verificar coordenador se informado
        if projeto_data.coordenador_id:
            coordenador = db.query(Usuario).filter(Usuario.id == projeto_data.coordenador_id).first()
            if not coordenador:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Coordenador com ID {projeto_data.coordenador_id} não encontrado"
                )
        
        # Calcular duração em meses
        duracao_meses = (projeto_data.data_termino.year - projeto_data.data_inicio.year) * 12 + \
                       (projeto_data.data_termino.month - projeto_data.data_inicio.month)
        
        # Extrair executoras
        executoras_data = projeto_data.dict().pop('executoras', [])
        
        # Criar projeto
        projeto = Projeto(
            **projeto_data.dict(exclude={'executoras'}),
            duracao_meses=duracao_meses,
            created_by=user_id
        )
        
        db.add(projeto)
        db.flush()  # Para obter o ID do projeto
        
        # Adicionar executoras
        if executoras_data:
            for exec_data in executoras_data:
                ProjetoService.add_executora(
                    db, 
                    projeto.id, 
                    exec_data['executora_id'],
                    exec_data.get('papel', 'Executora Principal'),
                    exec_data.get('percentual_participacao', 0),
                    user_id
                )
        
        db.commit()
        db.refresh(projeto)
        
        return projeto
    
    
    @staticmethod
    def update(
        db: Session, 
        projeto_id: int, 
        projeto_data: ProjetoUpdate, 
        user_id: int = None
    ) -> Projeto:
        """
        Atualiza projeto
        
        Args:
            db: Sessão do banco
            projeto_id: ID do projeto
            projeto_data: Dados para atualização
            user_id: ID do usuário que está atualizando
            
        Returns:
            Projeto atualizado
            
        Raises:
            HTTPException: Se projeto não encontrado
        """
        projeto = ProjetoService.get_by_id(db, projeto_id)
        
        if not projeto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Projeto com ID {projeto_id} não encontrado"
            )
        
        # Atualizar campos
        update_data = projeto_data.dict(exclude_unset=True)
        
        # Recalcular duração se datas mudaram
        if 'data_inicio' in update_data or 'data_termino' in update_data:
            data_inicio = update_data.get('data_inicio', projeto.data_inicio)
            data_termino = update_data.get('data_termino', projeto.data_termino)
            
            duracao_meses = (data_termino.year - data_inicio.year) * 12 + \
                           (data_termino.month - data_inicio.month)
            
            update_data['duracao_meses'] = duracao_meses
        
        for field, value in update_data.items():
            setattr(projeto, field, value)
        
        projeto.updated_by = user_id
        
        db.commit()
        db.refresh(projeto)
        
        return projeto
    
    
    @staticmethod
    def delete(db: Session, projeto_id: int) -> bool:
        """
        Deleta projeto (soft delete)
        
        Args:
            db: Sessão do banco
            projeto_id: ID do projeto
            
        Returns:
            True se deletado com sucesso
            
        Raises:
            HTTPException: Se projeto não encontrado
        """
        projeto = ProjetoService.get_by_id(db, projeto_id)
        
        if not projeto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Projeto com ID {projeto_id} não encontrado"
            )
        
        projeto.ativo = False
        db.commit()
        
        return True
    
    
    @staticmethod
    def add_executora(
        db: Session,
        projeto_id: int,
        executora_id: int,
        papel: str = "Executora Principal",
        percentual: float = 0,
        user_id: int = None
    ) -> ProjetoExecutora:
        """
        Adiciona executora ao projeto
        
        Args:
            db: Sessão do banco
            projeto_id: ID do projeto
            executora_id: ID da executora
            papel: Papel da executora
            percentual: Percentual de participação
            user_id: ID do usuário
            
        Returns:
            ProjetoExecutora criado
            
        Raises:
            HTTPException: Se projeto ou executora não encontrados
        """
        # Verificar se projeto existe
        projeto = ProjetoService.get_by_id(db, projeto_id)
        if not projeto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Projeto com ID {projeto_id} não encontrado"
            )
        
        # Verificar se executora existe
        executora = db.query(Executora).filter(Executora.id == executora_id).first()
        if not executora:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Executora com ID {executora_id} não encontrada"
            )
        
        # Verificar se já existe vínculo
        existing = db.query(ProjetoExecutora).filter(
            and_(
                ProjetoExecutora.projeto_id == projeto_id,
                ProjetoExecutora.executora_id == executora_id
            )
        ).first()
        
        if existing:
            # Reativar se estava inativo
            existing.ativo = True
            existing.papel = papel
            existing.percentual_participacao = percentual
            db.commit()
            db.refresh(existing)
            return existing
        
        # Criar novo vínculo
        projeto_executora = ProjetoExecutora(
            projeto_id=projeto_id,
            executora_id=executora_id,
            papel=papel,
            percentual_participacao=percentual,
            created_by=user_id
        )
        
        db.add(projeto_executora)
        db.commit()
        db.refresh(projeto_executora)
        
        return projeto_executora
    
    
    @staticmethod
    def remove_executora(db: Session, projeto_id: int, executora_id: int) -> bool:
        """
        Remove executora do projeto
        
        Args:
            db: Sessão do banco
            projeto_id: ID do projeto
            executora_id: ID da executora
            
        Returns:
            True se removido com sucesso
            
        Raises:
            HTTPException: Se vínculo não encontrado
        """
        projeto_executora = db.query(ProjetoExecutora).filter(
            and_(
                ProjetoExecutora.projeto_id == projeto_id,
                ProjetoExecutora.executora_id == executora_id
            )
        ).first()
        
        if not projeto_executora:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vínculo não encontrado"
            )
        
        projeto_executora.ativo = False
        db.commit()
        
        return True
    
    
    @staticmethod
    def get_executoras(db: Session, projeto_id: int) -> List[ProjetoExecutora]:
        """
        Lista executoras do projeto
        
        Args:
            db: Sessão do banco
            projeto_id: ID do projeto
            
        Returns:
            Lista de executoras vinculadas
        """
        return db.query(ProjetoExecutora).filter(
            and_(
                ProjetoExecutora.projeto_id == projeto_id,
                ProjetoExecutora.ativo == True
            )
        ).all()
    
    
    @staticmethod
    def get_projeto_detalhado(db: Session, projeto_id: int) -> dict:
        """
        Retorna projeto com todos os dados relacionados
        
        Args:
            db: Sessão do banco
            projeto_id: ID do projeto
            
        Returns:
            Dicionário com dados completos do projeto
        """
        projeto = ProjetoService.get_by_id(db, projeto_id)
        
        if not projeto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Projeto com ID {projeto_id} não encontrado"
            )
        
        # Buscar dados relacionados
        empresa = db.query(Empresa).filter(Empresa.id == projeto.empresa_id).first()
        coordenador = None
        if projeto.coordenador_id:
            coordenador = db.query(Usuario).filter(Usuario.id == projeto.coordenador_id).first()
        
        executoras = db.query(ProjetoExecutora, Executora).join(
            Executora, ProjetoExecutora.executora_id == Executora.id
        ).filter(
            and_(
                ProjetoExecutora.projeto_id == projeto_id,
                ProjetoExecutora.ativo == True
            )
        ).all()
        
        # Montar resposta
        return {
            **projeto.__dict__,
            'empresa_nome': empresa.nome if empresa else None,
            'empresa_sigla': empresa.sigla if empresa else None,
            'coordenador_nome': coordenador.nome if coordenador else None,
            'executoras': [
                {
                    'id': pe.id,
                    'executora_id': pe.executora_id,
                    'executora_nome': exec.nome,
                    'executora_sigla': exec.sigla,
                    'executora_tipo': exec.tipo,
                    'papel': pe.papel,
                    'percentual_participacao': float(pe.percentual_participacao),
                    'ativo': pe.ativo
                }
                for pe, exec in executoras
            ],
            'saldo_disponivel': float(projeto.saldo_disponivel),
            'percentual_tempo_decorrido': projeto.percentual_tempo_decorrido,
            'status_execucao': projeto.status_execucao
        }