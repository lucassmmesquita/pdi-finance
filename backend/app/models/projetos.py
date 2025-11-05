"""
PDI Finance - Project Model
Modelo SQLAlchemy para projetos PD&I
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import date

from app.db.base import Base, TimestampMixin


class Projeto(Base, TimestampMixin):
    """
    Model para tabela projetos
    Projetos de Pesquisa, Desenvolvimento e Inovação
    """
    __tablename__ = "projetos"
    
    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    
    # Identificação do Projeto
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nome = Column(String(200), nullable=False)
    sigla = Column(String(50), nullable=False)
    descricao = Column(Text)
    
    # Relacionamentos
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False, index=True)
    coordenador_id = Column(Integer, ForeignKey('usuarios.id'), index=True)
    
    # Classificação
    tipo = Column(String(20), nullable=False, index=True)  # CATI ou CAPDA
    area_conhecimento = Column(String(100))
    
    # Datas
    data_inicio = Column(Date, nullable=False)
    data_termino = Column(Date, nullable=False)
    duracao_meses = Column(Integer, nullable=False)
    
    # Financeiro
    valor_total = Column(Numeric(15, 2), nullable=False)
    valor_executado = Column(Numeric(15, 2), default=0)
    moeda = Column(String(3), default='BRL')
    
    # Aportes
    numero_parcelas = Column(Integer, nullable=False)
    
    # Status
    status = Column(
        String(30), 
        nullable=False, 
        default='Planejamento',
        index=True
    )
    percentual_execucao = Column(Numeric(5, 2), default=0)
    
    # Agência Financiadora
    agencia_financiadora = Column(String(100))
    numero_contrato = Column(String(100))
    
    # Observações
    observacoes = Column(Text)
    
    # Controle
    ativo = Column(Boolean, default=True, nullable=False, index=True)
    
    # Auditoria
    created_by = Column(Integer)
    updated_by = Column(Integer)
    
    # Relacionamentos
    # empresa = relationship("Empresa", back_populates="projetos")
    # coordenador = relationship("Usuario", foreign_keys=[coordenador_id])
    # executoras = relationship("ProjetoExecutora", back_populates="projeto", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Projeto(id={self.id}, codigo='{self.codigo}', nome='{self.nome}')>"
    
    @property
    def nome_completo(self) -> str:
        """Retorna nome com código"""
        return f"{self.codigo} - {self.nome}"
    
    @property
    def dias_projeto(self) -> int:
        """Calcula total de dias do projeto"""
        if self.data_inicio and self.data_termino:
            return (self.data_termino - self.data_inicio).days
        return 0
    
    @property
    def dias_decorridos(self) -> int:
        """Calcula dias decorridos desde o início"""
        if self.data_inicio:
            hoje = date.today()
            if hoje < self.data_inicio:
                return 0
            elif hoje > self.data_termino:
                return self.dias_projeto
            return (hoje - self.data_inicio).days
        return 0
    
    @property
    def percentual_tempo_decorrido(self) -> float:
        """Calcula percentual de tempo decorrido"""
        if self.dias_projeto > 0:
            return round((self.dias_decorridos / self.dias_projeto) * 100, 2)
        return 0
    
    @property
    def saldo_disponivel(self) -> float:
        """Calcula saldo disponível do projeto"""
        return float(self.valor_total - self.valor_executado)
    
    @property
    def status_execucao(self) -> str:
        """Retorna status de execução baseado em tempo vs orçamento"""
        tempo_decorrido = self.percentual_tempo_decorrido
        exec_orcamento = float(self.percentual_execucao)
        
        if exec_orcamento >= tempo_decorrido:
            return "No prazo"
        elif exec_orcamento < tempo_decorrido - 10:
            return "Atrasado"
        else:
            return "Atenção"


class ProjetoExecutora(Base):
    """
    Model para tabela projeto_executoras
    Relacionamento N:N entre Projetos e Executoras
    """
    __tablename__ = "projeto_executoras"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relacionamentos
    projeto_id = Column(Integer, ForeignKey('projetos.id', ondelete='CASCADE'), nullable=False, index=True)
    executora_id = Column(Integer, ForeignKey('executoras.id'), nullable=False, index=True)
    
    # Papel da Executora
    papel = Column(String(50), nullable=False, default='Executora Principal')
    
    # Percentual de Participação
    percentual_participacao = Column(Numeric(5, 2), default=0)
    
    # Período de Atuação
    data_inicio = Column(Date)
    data_termino = Column(Date)
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Auditoria
    created_at = Column(DateTime, nullable=False, server_default='NOW()')
    created_by = Column(Integer)
    
    # Relacionamentos
    # projeto = relationship("Projeto", back_populates="executoras")
    # executora = relationship("Executora", back_populates="projetos")
    
    def __repr__(self):
        return f"<ProjetoExecutora(projeto_id={self.projeto_id}, executora_id={self.executora_id}, papel='{self.papel}')>"