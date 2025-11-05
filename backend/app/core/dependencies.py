"""
PDI Finance - FastAPI Dependencies
Dependências reutilizáveis para injeção em endpoints
"""

from typing import Optional, Generator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.security import decode_token, verify_token_type
from app.models.user import Usuario
from app.schemas.user import UserInDB


# ==========================================
# DATABASE SESSION
# ==========================================

def get_db() -> Generator:
    """
    Dependency para obter sessão do banco de dados
    Garante que a sessão seja fechada após o request
    
    Yields:
        Session SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# AUTHENTICATION
# ==========================================

# Security scheme para Swagger UI
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserInDB:
    """
    Dependency para obter usuário autenticado atual
    Valida o token JWT e retorna dados do usuário
    
    Args:
        credentials: Token Bearer do header Authorization
        db: Sessão do banco de dados
        
    Returns:
        UserInDB: Dados completos do usuário
        
    Raises:
        HTTPException 401: Se token inválido ou usuário não encontrado
    """
    # Extrair token
    token = credentials.credentials
    
    # Decodificar token
    payload = decode_token(token)
    
    # Verificar tipo do token
    if not verify_token_type(payload, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extrair user_id (sub é string, converter para int)
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: usuário não identificado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: ID de usuário inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Buscar usuário no banco
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar se usuário está ativo
    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo. Entre em contato com o administrador.",
        )
    
    # Verificar se usuário está bloqueado
    from datetime import datetime
    if user.bloqueado_ate and user.bloqueado_ate > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário temporariamente bloqueado devido a múltiplas tentativas de login falhas.",
        )
    
    return UserInDB.from_orm(user)


def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """
    Dependency para garantir que o usuário está ativo
    (redundante com get_current_user, mas útil para clareza)
    
    Args:
        current_user: Usuário atual autenticado
        
    Returns:
        UserInDB: Usuário ativo
    """
    return current_user


# ==========================================
# ROLE-BASED ACCESS CONTROL (RBAC)
# ==========================================

def require_admin(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """
    Dependency para restringir acesso apenas a Admins
    
    Args:
        current_user: Usuário atual autenticado
        
    Returns:
        UserInDB: Usuário com perfil Admin
        
    Raises:
        HTTPException 403: Se usuário não for Admin
    """
    if current_user.perfil != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem realizar esta ação.",
        )
    return current_user


def require_gestor_or_admin(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """
    Dependency para restringir acesso a Gestores ou Admins
    
    Args:
        current_user: Usuário atual autenticado
        
    Returns:
        UserInDB: Usuário com perfil Gestor ou Admin
        
    Raises:
        HTTPException 403: Se usuário não tiver permissão
    """
    if current_user.perfil not in ["Admin", "Gestor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas gestores ou administradores podem realizar esta ação.",
        )
    return current_user


def require_coordenador_or_above(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """
    Dependency para restringir acesso a Coordenadores, Gestores ou Admins
    
    Args:
        current_user: Usuário atual autenticado
        
    Returns:
        UserInDB: Usuário com permissão adequada
        
    Raises:
        HTTPException 403: Se usuário não tiver permissão
    """
    if current_user.perfil not in ["Admin", "Gestor", "Coordenador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Permissão insuficiente.",
        )
    return current_user


# ==========================================
# OPTIONAL AUTHENTICATION
# ==========================================

def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[UserInDB]:
    """
    Dependency para obter usuário se autenticado, None caso contrário
    Útil para endpoints públicos que podem ter comportamento diferente se autenticado
    
    Args:
        request: Request FastAPI
        db: Sessão do banco de dados
        
    Returns:
        UserInDB ou None
    """
    # Verificar se há header Authorization
    authorization = request.headers.get("Authorization")
    
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
        
        if not verify_token_type(payload, "access"):
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = db.query(Usuario).filter(Usuario.id == user_id, Usuario.ativo == True).first()
        
        if user:
            return UserInDB.from_orm(user)
        
    except Exception:
        pass
    
    return None


# ==========================================
# RATE LIMITING (Future Implementation)
# ==========================================

def check_rate_limit(request: Request) -> None:
    """
    Dependency para verificar rate limiting
    TODO: Implementar com Redis ou similar
    
    Args:
        request: Request FastAPI
        
    Raises:
        HTTPException 429: Se exceder limite de requisições
    """
    # Placeholder para futura implementação
    pass