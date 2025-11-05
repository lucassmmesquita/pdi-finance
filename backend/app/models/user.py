"""
PDI Finance - User Model
Modelo SQLAlchemy para tabela usuarios
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base, TimestampMixin


class Usuario(Base, TimestampMixin):
    """
    Model para tabela usuarios
    """
    __tablename__ = "usuarios"
    
    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    
    # Dados Pessoais
    nome = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    
    # Autenticação
    senha_hash = Column(String(255), nullable=False)
    salt = Column(String(100), nullable=False)
    
    # Perfil e Permissões
    perfil = Column(String(20), nullable=False, index=True)  # Admin, Gestor, Coordenador, Consulta
    ativo = Column(Boolean, default=True, nullable=False, index=True)
    
    # Controle de Sessão
    ultimo_login = Column(DateTime(timezone=True), nullable=True)
    token_reset_senha = Column(String(255), nullable=True)
    token_reset_expira = Column(DateTime(timezone=True), nullable=True)
    tentativas_login = Column(Integer, default=0, nullable=False)
    bloqueado_ate = Column(DateTime(timezone=True), nullable=True)
    
    # Auditoria
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # Relacionamentos (serão adicionados conforme outros models)
    # sessoes = relationship("Sessao", back_populates="usuario", cascade="all, delete-orphan")
    # auditorias_login = relationship("AuditoriaLogin", back_populates="usuario")
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, email='{self.email}', perfil='{self.perfil}')>"
    
    @property
    def is_admin(self) -> bool:
        """Verifica se usuário é Admin"""
        return self.perfil == "Admin"
    
    @property
    def is_gestor(self) -> bool:
        """Verifica se usuário é Gestor"""
        return self.perfil == "Gestor"
    
    @property
    def is_coordenador(self) -> bool:
        """Verifica se usuário é Coordenador"""
        return self.perfil == "Coordenador"
    
    @property
    def can_manage_users(self) -> bool:
        """Verifica se usuário pode gerenciar outros usuários"""
        return self.perfil == "Admin"
    
    @property
    def can_manage_projects(self) -> bool:
        """Verifica se usuário pode gerenciar projetos"""
        return self.perfil in ["Admin", "Gestor", "Coordenador"]


class Sessao(Base):
    """
    Model para tabela sessoes
    Controle de sessões ativas (JWT tokens)
    """
    __tablename__ = "sessoes"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=False, index=True)
    token_jti = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    expira_em = Column(DateTime(timezone=True), nullable=False, index=True)
    revogado = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default='NOW()')
    
    # Relacionamento (será ativado quando Usuario tiver back_populates)
    # usuario = relationship("Usuario", back_populates="sessoes")
    
    def __repr__(self):
        return f"<Sessao(id={self.id}, usuario_id={self.usuario_id}, revogado={self.revogado})>"


class AuditoriaLogin(Base):
    """
    Model para tabela auditoria_login
    Log de todas as tentativas de login
    """
    __tablename__ = "auditoria_login"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=True, index=True)
    email_tentativa = Column(String(200), nullable=False)
    sucesso = Column(Boolean, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    mensagem = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default='NOW()', index=True)
    
    # Relacionamento (será ativado quando Usuario tiver back_populates)
    # usuario = relationship("Usuario", back_populates="auditorias_login")
    
    def __repr__(self):
        return f"<AuditoriaLogin(id={self.id}, email='{self.email_tentativa}', sucesso={self.sucesso})>"