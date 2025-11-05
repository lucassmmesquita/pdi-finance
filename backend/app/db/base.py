"""
PDI Finance - Database Base
Classe base declarativa para todos os models
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, func


# ==========================================
# BASE CLASS
# ==========================================

Base = declarative_base()


# ==========================================
# MIXIN CLASSES
# ==========================================

class TimestampMixin:
    """
    Mixin para adicionar campos de timestamp automáticos
    """
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class AuditMixin:
    """
    Mixin para adicionar campos de auditoria
    """
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
