"""
Script para testar login completo
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import bcrypt
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import Usuario
from app.services.auth_service import AuthService


def test_login():
    """Testa o processo completo de login"""
    
    db: Session = SessionLocal()
    
    try:
        print("\n" + "=" * 70)
        print("🧪 PDI Finance - Teste de Login")
        print("=" * 70)
        
        email = "admin@pdifinance.com"
        senha = "Admin@2025"
        
        # 1. Verificar usuário no banco
        print("\n1️⃣  Buscando usuário no banco...")
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        
        if not usuario:
            print(f"   ❌ Usuário {email} não encontrado!")
            print("\n   Execute primeiro: python scripts/reset_database.py")
            return
        
        print(f"   ✅ Usuário encontrado!")
        print(f"   ID: {usuario.id}")
        print(f"   Email: {usuario.email}")
        print(f"   Ativo: {usuario.ativo}")
        print(f"   Bloqueado: {usuario.bloqueado_ate}")
        print(f"   Tentativas: {usuario.tentativas_login}")
        
        # 2. Testar verificação de senha direta
        print("\n2️⃣  Testando verificação de senha (bcrypt direto)...")
        senha_bytes = senha.encode('utf-8')
        hash_bytes = usuario.senha_hash.encode('utf-8')
        
        try:
            resultado_bcrypt = bcrypt.checkpw(senha_bytes, hash_bytes)
            print(f"   Resultado bcrypt.checkpw: {resultado_bcrypt}")
            
            if resultado_bcrypt:
                print("   ✅ Senha correta (bcrypt direto)!")
            else:
                print("   ❌ Senha incorreta (bcrypt direto)!")
                return
        except Exception as e:
            print(f"   ❌ Erro no bcrypt: {e}")
            return
        
        # 3. Testar verify_password do security.py
        print("\n3️⃣  Testando verify_password do security.py...")
        from app.core.security import verify_password
        
        try:
            resultado_security = verify_password(senha, usuario.senha_hash)
            print(f"   Resultado verify_password: {resultado_security}")
            
            if resultado_security:
                print("   ✅ Senha correta (security.py)!")
            else:
                print("   ❌ Senha incorreta (security.py)!")
                return
        except Exception as e:
            print(f"   ❌ Erro no verify_password: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 4. Testar AuthService.authenticate_user
        print("\n4️⃣  Testando AuthService.authenticate_user...")
        
        try:
            usuario_auth, mensagem = AuthService.authenticate_user(
                db, email, senha, "127.0.0.1", "test-script"
            )
            
            print(f"   ✅ Autenticação bem-sucedida!")
            print(f"   Mensagem: {mensagem}")
            print(f"   Usuário ID: {usuario_auth.id}")
            print(f"   Tentativas resetadas: {usuario_auth.tentativas_login}")
            
        except Exception as e:
            print(f"   ❌ Erro na autenticação: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 5. Testar criação de tokens
        print("\n5️⃣  Testando criação de tokens...")
        
        try:
            response = AuthService.create_tokens(usuario_auth, db, "127.0.0.1", "test-script")
            
            print(f"   ✅ Tokens criados com sucesso!")
            print(f"   Access Token (início): {response.access_token[:50]}...")
            print(f"   Refresh Token (início): {response.refresh_token[:50]}...")
            print(f"   Expires in: {response.expires_in} segundos")
            print(f"   User ID: {response.user['id']}")
            print(f"   User Name: {response.user['nome']}")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar tokens: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 6. Resumo
        print("\n" + "=" * 70)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("=" * 70)
        print("\n🌐 Agora teste via HTTP:")
        print('curl -X POST "http://localhost:8000/api/v1/auth/login" \\')
        print('  -H "Content-Type: application/json" \\')
        print(f'  -d \'{{"email": "{email}", "senha": "{senha}"}}\'')
        print("\n📚 Ou acesse o Swagger: http://localhost:8000/docs")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_login()