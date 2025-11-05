"""
PDI Finance - Database Session
Configuração da sessão SQLAlchemy
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings


# ==========================================
# ENGINE
# ==========================================

# Criar engine do SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,  # Log de SQL queries (útil para debug)
    poolclass=QueuePool,
    pool_size=5,  # Número de conexões no pool
    max_overflow=10,  # Máximo de conexões adicionais
    pool_pre_ping=True,  # Verifica conexões antes de usar
    pool_recycle=3600,  # Recicla conexões após 1 hora
)


# ==========================================
# SESSION FACTORY
# ==========================================

# Criar factory de sessões
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==========================================
# UTILITIES
# ==========================================

def get_db_session():
    """
    Cria e retorna uma nova sessão do banco de dados
    
    Returns:
        Session: Sessão SQLAlchemy
    """
    return SessionLocal()


def test_connection() -> bool:
    """
    Testa a conexão com o banco de dados
    
    Returns:
        bool: True se conexão bem-sucedida
    """
    try:
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return False