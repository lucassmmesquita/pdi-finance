"""
PDI Finance - Authentication Service
Lógica de negócio para autenticação
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import Usuario, AuditoriaLogin, Sessao
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type
)
from app.core.config import settings
from app.schemas.auth import LoginResponse, RefreshTokenResponse


class AuthService:
    """Serviço de autenticação"""
    
    @staticmethod
    def authenticate_user(db: Session, email: str, senha: str, ip_address: str = None, user_agent: str = None) -> Tuple[Usuario, str]:
        """
        Autentica usuário e retorna usuário + mensagem
        
        Args:
            db: Sessão do banco
            email: Email do usuário
            senha: Senha em texto plano
            ip_address: IP do cliente
            user_agent: User agent do navegador
            
        Returns:
            Tuple[Usuario, mensagem]
            
        Raises:
            HTTPException: Se credenciais inválidas ou usuário bloqueado
        """
        # Buscar usuário
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        
        # Usuário não encontrado
        if not usuario:
            AuthService._registrar_tentativa_login(
                db, None, email, False, ip_address, user_agent, "Usuário não encontrado"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        # Verificar se usuário está ativo
        if not usuario.ativo:
            AuthService._registrar_tentativa_login(
                db, usuario.id, email, False, ip_address, user_agent, "Usuário inativo"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo. Entre em contato com o administrador."
            )
        
        # Verificar se usuário está bloqueado
        if usuario.bloqueado_ate and usuario.bloqueado_ate > datetime.utcnow():
            minutos_restantes = int((usuario.bloqueado_ate - datetime.utcnow()).total_seconds() / 60)
            AuthService._registrar_tentativa_login(
                db, usuario.id, email, False, ip_address, user_agent, 
                f"Usuário bloqueado por {minutos_restantes} minutos"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Usuário temporariamente bloqueado. Tente novamente em {minutos_restantes} minutos."
            )
        
        # Verificar senha (bcrypt compara diretamente)
        try:
            senha_valida = verify_password(senha, usuario.senha_hash)
        except Exception as e:
            # Se der erro na verificação, considera senha inválida
            senha_valida = False
        
        if not senha_valida:
            # Incrementar tentativas
            usuario.tentativas_login += 1
            
            # Bloquear após 5 tentativas
            if usuario.tentativas_login >= settings.MAX_LOGIN_ATTEMPTS:
                usuario.bloqueado_ate = datetime.utcnow() + timedelta(minutes=settings.LOGIN_BLOCK_MINUTES)
                db.commit()
                
                AuthService._registrar_tentativa_login(
                    db, usuario.id, email, False, ip_address, user_agent, 
                    f"Conta bloqueada por {settings.LOGIN_BLOCK_MINUTES} minutos"
                )
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Conta bloqueada por {settings.LOGIN_BLOCK_MINUTES} minutos devido a múltiplas tentativas falhas."
                )
            
            db.commit()
            tentativas_restantes = settings.MAX_LOGIN_ATTEMPTS - usuario.tentativas_login
            
            AuthService._registrar_tentativa_login(
                db, usuario.id, email, False, ip_address, user_agent, 
                f"Senha incorreta. Tentativas restantes: {tentativas_restantes}"
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Email ou senha incorretos. Tentativas restantes: {tentativas_restantes}"
            )
        
        # Login bem-sucedido - resetar tentativas e bloqueio
        usuario.tentativas_login = 0
        usuario.bloqueado_ate = None
        usuario.ultimo_login = datetime.utcnow()
        db.commit()
        
        AuthService._registrar_tentativa_login(
            db, usuario.id, email, True, ip_address, user_agent, "Login realizado com sucesso"
        )
        
        return usuario, "Login realizado com sucesso"
    
    
    @staticmethod
    def create_tokens(usuario: Usuario, db: Session, ip_address: str = None, user_agent: str = None) -> LoginResponse:
        """
        Cria tokens de acesso e refresh para o usuário
        
        Args:
            usuario: Usuário autenticado
            db: Sessão do banco
            ip_address: IP do cliente
            user_agent: User agent
            
        Returns:
            LoginResponse com tokens
        """
        # Dados para o token (sub deve ser string)
        token_data = {
            "sub": str(usuario.id),  # Converter para string
            "email": usuario.email,
            "perfil": usuario.perfil
        }
        
        # Criar tokens
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Decodificar para pegar JTI e expiration
        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)
        
        # Salvar sessão de access token
        sessao_access = Sessao(
            usuario_id=usuario.id,
            token_jti=access_payload["jti"],
            ip_address=ip_address,
            user_agent=user_agent,
            expira_em=datetime.fromtimestamp(access_payload["exp"]),
            revogado=False
        )
        db.add(sessao_access)
        
        # Salvar sessão de refresh token
        sessao_refresh = Sessao(
            usuario_id=usuario.id,
            token_jti=refresh_payload["jti"],
            ip_address=ip_address,
            user_agent=user_agent,
            expira_em=datetime.fromtimestamp(refresh_payload["exp"]),
            revogado=False
        )
        db.add(sessao_refresh)
        db.commit()
        
        # Montar resposta
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": usuario.id,
                "uuid": str(usuario.uuid),
                "nome": usuario.nome,
                "email": usuario.email,
                "perfil": usuario.perfil
            }
        )
    
    
    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> RefreshTokenResponse:
        """
        Gera novo access token a partir de um refresh token válido
        
        Args:
            db: Sessão do banco
            refresh_token: Refresh token
            
        Returns:
            RefreshTokenResponse com novo access token
            
        Raises:
            HTTPException: Se refresh token inválido
        """
        # Decodificar refresh token
        try:
            payload = decode_token(refresh_token)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido ou expirado"
            )
        
        # Verificar tipo do token
        if not verify_token_type(payload, "refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: não é um refresh token"
            )
        
        # Verificar se sessão existe e não foi revogada
        jti = payload.get("jti")
        sessao = db.query(Sessao).filter(Sessao.token_jti == jti).first()
        
        if not sessao or sessao.revogado:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sessão inválida ou revogada"
            )
        
        # Buscar usuário
        user_id = payload.get("sub")
        usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
        
        if not usuario or not usuario.ativo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado ou inativo"
            )
        
        # Criar novo access token
        token_data = {
            "sub": usuario.id,
            "email": usuario.email,
            "perfil": usuario.perfil
        }
        
        new_access_token = create_access_token(token_data)
        access_payload = decode_token(new_access_token)
        
        # Salvar nova sessão
        nova_sessao = Sessao(
            usuario_id=usuario.id,
            token_jti=access_payload["jti"],
            ip_address=sessao.ip_address,
            user_agent=sessao.user_agent,
            expira_em=datetime.fromtimestamp(access_payload["exp"]),
            revogado=False
        )
        db.add(nova_sessao)
        db.commit()
        
        return RefreshTokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    
    @staticmethod
    def logout(db: Session, token_jti: str) -> dict:
        """
        Revoga a sessão do usuário (logout)
        
        Args:
            db: Sessão do banco
            token_jti: JTI do token atual
            
        Returns:
            Dict com mensagem de sucesso
        """
        # Buscar sessão
        sessao = db.query(Sessao).filter(Sessao.token_jti == token_jti).first()
        
        if sessao:
            sessao.revogado = True
            db.commit()
        
        return {
            "message": "Logout realizado com sucesso",
            "logged_out_at": datetime.utcnow()
        }
    
    
    @staticmethod
    def _registrar_tentativa_login(
        db: Session,
        usuario_id: Optional[int],
        email: str,
        sucesso: bool,
        ip_address: Optional[str],
        user_agent: Optional[str],
        mensagem: str
    ):
        """
        Registra tentativa de login na auditoria
        
        Args:
            db: Sessão do banco
            usuario_id: ID do usuário (pode ser None se não encontrado)
            email: Email da tentativa
            sucesso: Se login foi bem-sucedido
            ip_address: IP do cliente
            user_agent: User agent
            mensagem: Mensagem descritiva
        """
        auditoria = AuditoriaLogin(
            usuario_id=usuario_id,
            email_tentativa=email,
            sucesso=sucesso,
            ip_address=ip_address,
            user_agent=user_agent,
            mensagem=mensagem,
            created_at=datetime.utcnow()
        )
        db.add(auditoria)
        db.commit()