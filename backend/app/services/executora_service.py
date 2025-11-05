"""
PDI Finance - Executora Service
Lógica de negócio para executoras e empresas
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.executora import Executora, Empresa
from app.schemas.executora import ExecutoraCreate, ExecutoraUpdate, EmpresaCreate, EmpresaUpdate


class ExecutoraService:
    """Serviço para gerenciar executoras"""
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100, ativo: Optional[bool] = None) -> List[Executora]:
        """
        Lista todas as executoras
        
        Args:
            db: Sessão do banco
            skip: Número de registros para pular
            limit: Limite de registros
            ativo: Filtrar por status ativo
            
        Returns:
            Lista de executoras
        """
        query = db.query(Executora)
        
        if ativo is not None:
            query = query.filter(Executora.ativo == ativo)
        
        return query.offset(skip).limit(limit).all()
    
    
    @staticmethod
    def get_by_id(db: Session, executora_id: int) -> Optional[Executora]:
        """
        Busca executora por ID
        
        Args:
            db: Sessão do banco
            executora_id: ID da executora
            
        Returns:
            Executora encontrada ou None
        """
        return db.query(Executora).filter(Executora.id == executora_id).first()
    
    
    @staticmethod
    def get_by_sigla(db: Session, sigla: str) -> Optional[Executora]:
        """
        Busca executora por sigla
        
        Args:
            db: Sessão do banco
            sigla: Sigla da executora
            
        Returns:
            Executora encontrada ou None
        """
        return db.query(Executora).filter(Executora.sigla == sigla).first()
    
    
    @staticmethod
    def get_by_tipo(db: Session, tipo: str) -> List[Executora]:
        """
        Lista executoras por tipo
        
        Args:
            db: Sessão do banco
            tipo: Tipo da executora (IREDE, IES, ICT, Outro)
            
        Returns:
            Lista de executoras do tipo especificado
        """
        return db.query(Executora).filter(
            Executora.tipo == tipo,
            Executora.ativo == True
        ).all()
    
    
    @staticmethod
    def create(db: Session, executora_data: ExecutoraCreate, user_id: int = None) -> Executora:
        """
        Cria nova executora
        
        Args:
            db: Sessão do banco
            executora_data: Dados da executora
            user_id: ID do usuário criador
            
        Returns:
            Executora criada
            
        Raises:
            HTTPException: Se sigla já existe
        """
        # Verificar se sigla já existe
        existing = ExecutoraService.get_by_sigla(db, executora_data.sigla)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Executora com sigla '{executora_data.sigla}' já existe"
            )
        
        # Criar executora
        executora = Executora(
            **executora_data.dict(),
            created_by=user_id
        )
        
        db.add(executora)
        db.commit()
        db.refresh(executora)
        
        return executora
    
    
    @staticmethod
    def update(
        db: Session, 
        executora_id: int, 
        executora_data: ExecutoraUpdate, 
        user_id: int = None
    ) -> Executora:
        """
        Atualiza executora
        
        Args:
            db: Sessão do banco
            executora_id: ID da executora
            executora_data: Dados para atualização
            user_id: ID do usuário que está atualizando
            
        Returns:
            Executora atualizada
            
        Raises:
            HTTPException: Se executora não encontrada
        """
        executora = ExecutoraService.get_by_id(db, executora_id)
        
        if not executora:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Executora com ID {executora_id} não encontrada"
            )
        
        # Atualizar campos
        update_data = executora_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(executora, field, value)
        
        executora.updated_by = user_id
        
        db.commit()
        db.refresh(executora)
        
        return executora
    
    
    @staticmethod
    def delete(db: Session, executora_id: int) -> bool:
        """
        Deleta executora (soft delete)
        
        Args:
            db: Sessão do banco
            executora_id: ID da executora
            
        Returns:
            True se deletado com sucesso
            
        Raises:
            HTTPException: Se executora não encontrada
        """
        executora = ExecutoraService.get_by_id(db, executora_id)
        
        if not executora:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Executora com ID {executora_id} não encontrada"
            )
        
        executora.ativo = False
        db.commit()
        
        return True


class EmpresaService:
    """Serviço para gerenciar empresas"""
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100, ativo: Optional[bool] = None) -> List[Empresa]:
        """Lista todas as empresas"""
        query = db.query(Empresa)
        
        if ativo is not None:
            query = query.filter(Empresa.ativo == ativo)
        
        return query.offset(skip).limit(limit).all()
    
    
    @staticmethod
    def get_by_id(db: Session, empresa_id: int) -> Optional[Empresa]:
        """Busca empresa por ID"""
        return db.query(Empresa).filter(Empresa.id == empresa_id).first()
    
    
    @staticmethod
    def get_by_sigla(db: Session, sigla: str) -> Optional[Empresa]:
        """Busca empresa por sigla"""
        return db.query(Empresa).filter(Empresa.sigla == sigla).first()
    
    
    @staticmethod
    def create(db: Session, empresa_data: EmpresaCreate, user_id: int = None) -> Empresa:
        """Cria nova empresa"""
        # Verificar se sigla já existe
        existing = EmpresaService.get_by_sigla(db, empresa_data.sigla)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Empresa com sigla '{empresa_data.sigla}' já existe"
            )
        
        empresa = Empresa(
            **empresa_data.dict(),
            created_by=user_id
        )
        
        db.add(empresa)
        db.commit()
        db.refresh(empresa)
        
        return empresa
    
    
    @staticmethod
    def update(
        db: Session, 
        empresa_id: int, 
        empresa_data: EmpresaUpdate, 
        user_id: int = None
    ) -> Empresa:
        """Atualiza empresa"""
        empresa = EmpresaService.get_by_id(db, empresa_id)
        
        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Empresa com ID {empresa_id} não encontrada"
            )
        
        update_data = empresa_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(empresa, field, value)
        
        empresa.updated_by = user_id
        
        db.commit()
        db.refresh(empresa)
        
        return empresa
    
    
    @staticmethod
    def delete(db: Session, empresa_id: int) -> bool:
        """Deleta empresa (soft delete)"""
        empresa = EmpresaService.get_by_id(db, empresa_id)
        
        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Empresa com ID {empresa_id} não encontrada"
            )
        
        empresa.ativo = False
        db.commit()
        
        return True