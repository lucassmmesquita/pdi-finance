"""
PDI Finance - Executora Model
Modelo SQLAlchemy para executoras dos projetos
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base, TimestampMixin


class Executora(Base, TimestampMixin):
    """
    Model para tabela executoras
    Instituições que executam os projetos (IREDE, Universidades, etc)
    """
    __tablename__ = "executoras"
    
    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    
    # Dados da Executora
    nome = Column(String(200), nullable=False)
    sigla = Column(String(50), nullable=False)
    tipo = Column(String(50), nullable=False)  # IREDE, IES, ICT, Outro
    
    # Localização
    cidade = Column(String(100))
    estado = Column(String(2))
    
    # Contato
    email = Column(String(200))
    telefone = Column(String(20))
    responsavel = Column(String(200))
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False, index=True)
    
    # Auditoria
    created_by = Column(Integer)
    updated_by = Column(Integer)
    
    # Relacionamentos
    # projetos = relationship("ProjetoExecutora", back_populates="executora")
    
    def __repr__(self):
        return f"<Executora(id={self.id}, nome='{self.nome}', tipo='{self.tipo}')>"
    
    @property
    def nome_completo(self) -> str:
        """Retorna nome com sigla"""
        return f"{self.nome} ({self.sigla})"
    
    @property
    def localizacao(self) -> str:
        """Retorna localização formatada"""
        if self.cidade and self.estado:
            return f"{self.cidade}/{self.estado}"
        return self.estado or self.cidade or "N/A"


class Empresa(Base, TimestampMixin):
    """
    Model para tabela empresas
    Empresas financiadoras dos projetos
    """
    __tablename__ = "empresas"
    
    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    
    # Dados da Empresa
    nome = Column(String(200), nullable=False)
    sigla = Column(String(50), nullable=False, index=True)
    cnpj = Column(String(18), unique=True)
    
    # Contato
    email = Column(String(200))
    telefone = Column(String(20))
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False, index=True)
    
    # Auditoria
    created_by = Column(Integer)
    updated_by = Column(Integer)
    
    # Relacionamentos
    # projetos = relationship("Projeto", back_populates="empresa")
    
    def __repr__(self):
        return f"<Empresa(id={self.id}, nome='{self.nome}', sigla='{self.sigla}')>"
    
    @property
    def nome_completo(self) -> str:
        """Retorna nome com sigla"""
        return f"{self.nome} ({self.sigla})"