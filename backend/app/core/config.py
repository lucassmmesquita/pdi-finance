"""
PDI Finance - Core Configuration
Gerenciamento de variáveis de ambiente e configurações globais
"""

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Informações do Projeto
    PROJECT_NAME: str = "PDI Finance API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Sistema de Controle Orçamentário e Financeiro de Projetos PD&I"
    API_V1_PREFIX: str = "/api/v1"
    
    # Ambiente
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Banco de Dados PostgreSQL
    DATABASE_URL: str = "postgresql://pdi_user:pdi_password@localhost:5432/pdi_finance"
    DB_ECHO: bool = False  # Log de queries SQL (útil para debug)
    
    # JWT Authentication
    SECRET_KEY: str = "sua-chave-secreta-super-segura-mude-em-producao-123456789"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # React default
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    # Upload de Arquivos
    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_EXTENSIONS: List[str] = [".xlsx", ".xls", ".xlsm"]
    
    # Segurança
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
    # Rate Limiting
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_BLOCK_MINUTES: int = 15
    
    # Paginação
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna instância única de Settings (singleton)
    Cached para melhor performance
    """
    return Settings()


# Instância global
settings = get_settings()
