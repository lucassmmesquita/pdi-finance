"""
PDI Finance - Authentication Endpoints
Rotas de autenticação (login, logout, refresh, me)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutResponse,
    CurrentUserResponse
)
from app.schemas.user import UserInDB
from app.services.auth_service import AuthService
from app.core.security import decode_token


# Criar router
router = APIRouter(prefix="/auth", tags=["Autenticação"])


# ==========================================
# POST /auth/login
# ==========================================

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login de usuário",
    description="Autentica usuário e retorna tokens de acesso (JWT)"
)
def login(
    credentials: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    **Endpoint de Login**
    
    Autentica o usuário com email e senha, retornando:
    - Access Token (JWT) - válido por 30 minutos
    - Refresh Token (JWT) - válido por 7 dias
    - Dados básicos do usuário
    
    **Segurança:**
    - Após 5 tentativas falhas, a conta é bloqueada por 15 minutos
    - Todas as tentativas são registradas na auditoria
    
    **Exemplo de uso:**
    ```json
    {
        "email": "admin@pdifinance.com",
        "senha": "Admin@2025"
    }
    ```
    """
    try:
        # Extrair IP e User Agent
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Autenticar usuário
        usuario, mensagem = AuthService.authenticate_user(
            db, credentials.email, credentials.senha, ip_address, user_agent
        )
        
        # Criar tokens
        response = AuthService.create_tokens(usuario, db, ip_address, user_agent)
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar login: {str(e)}"
        )


# ==========================================
# POST /auth/refresh
# ==========================================

@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Renovar access token",
    description="Gera novo access token usando refresh token válido"
)
def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    **Endpoint de Refresh Token**
    
    Gera um novo access token a partir de um refresh token válido.
    Use este endpoint quando o access token expirar (após 30 minutos).
    
    **Como usar:**
    1. O frontend detecta que o access token expirou (erro 401)
    2. Envia o refresh token armazenado
    3. Recebe novo access token válido
    4. Continua usando a aplicação sem novo login
    
    **Exemplo de uso:**
    ```json
    {
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```
    """
    response = AuthService.refresh_access_token(db, refresh_request.refresh_token)
    return response


# ==========================================
# POST /auth/logout
# ==========================================

@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout de usuário",
    description="Revoga a sessão atual do usuário"
)
def logout(
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    **Endpoint de Logout**
    
    Revoga a sessão atual do usuário, invalidando o token.
    Requer token de acesso válido no header Authorization.
    
    **Como usar:**
    ```
    Authorization: Bearer {seu_access_token}
    ```
    
    **Após logout:**
    - O token atual não poderá mais ser usado
    - O usuário precisará fazer login novamente
    - O refresh token também é invalidado
    """
    # Extrair JTI do token atual
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
        token_jti = payload.get("jti")
        
        # Fazer logout
        result = AuthService.logout(db, token_jti)
        return result
    
    return {
        "message": "Logout realizado com sucesso",
        "logged_out_at": "now"
    }


# ==========================================
# GET /auth/me
# ==========================================

@router.get(
    "/me",
    response_model=CurrentUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Obter usuário atual",
    description="Retorna dados do usuário autenticado"
)
def get_me(current_user: UserInDB = Depends(get_current_user)):
    """
    **Endpoint de Usuário Atual**
    
    Retorna informações completas do usuário autenticado.
    Útil para:
    - Carregar dados do usuário após login
    - Verificar se token ainda é válido
    - Obter permissões do usuário
    
    **Requer:**
    ```
    Authorization: Bearer {seu_access_token}
    ```
    
    **Retorna:**
    - Dados pessoais do usuário
    - Perfil e permissões
    - Data do último login
    """
    # Calcular permissões baseadas no perfil
    permissions = {
        "can_manage_users": current_user.perfil == "Admin",
        "can_manage_projects": current_user.perfil in ["Admin", "Gestor", "Coordenador"],
        "can_import_files": current_user.perfil in ["Admin", "Gestor", "Coordenador"],
        "can_export_reports": current_user.perfil in ["Admin", "Gestor", "Coordenador"],
        "can_view_dashboard": True,
        "can_edit_expenses": current_user.perfil in ["Admin", "Gestor"],
        "can_approve_expenses": current_user.perfil in ["Admin", "Gestor"],
    }
    
    return CurrentUserResponse(
        id=current_user.id,
        uuid=str(current_user.uuid),
        nome=current_user.nome,
        email=current_user.email,
        perfil=current_user.perfil,
        ativo=current_user.ativo,
        ultimo_login=current_user.ultimo_login,
        created_at=current_user.created_at,
        permissions=permissions
    )


# ==========================================
# GET /auth/health
# ==========================================

@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Verifica se o serviço de autenticação está funcionando"
)
def health_check():
    """
    **Health Check**
    
    Endpoint simples para verificar se o serviço está online.
    Usado para monitoramento e load balancers.
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "version": "1.0.0"
    }