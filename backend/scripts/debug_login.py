"""
Script para debugar e corrigir problemas de login
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import Usuario
from app.core.security import hash_password, verify_password, generate_salt
from datetime import datetime
import uuid


def debug_login():
    """Debug completo do sistema de login"""
    
    db: Session = SessionLocal()
    
    try:
        print("\n" + "=" * 70)
        print("🔍 PDI Finance - Debug de Login")
        print("=" * 70)
        
        email = "admin@pdifinance.com"
        senha_teste = "Admin@2025"
        
        # 1. Buscar usuário
        print("\n1️⃣  Buscando usuário no banco...")
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        
        if not usuario:
            print(f"❌ Usuário {email} não encontrado no banco!")
            print("\n🔧 Criando novo usuário admin...")
            
            # Criar usuário
            novo_usuario = Usuario(
                uuid=uuid.uuid4(),
                nome="Administrador do Sistema",
                email=email,
                senha_hash=hash_password(senha_teste),
                salt=generate_salt(),
                perfil="Admin",
                ativo=True,
                tentativas_login=0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(novo_usuario)
            db.commit()
            db.refresh(novo_usuario)
            
            print("✅ Usuário criado com sucesso!")
            print(f"   ID: {novo_usuario.id}")
            print(f"   Email: {novo_usuario.email}")
            print(f"   Senha: {senha_teste}")
            return
        
        print(f"✅ Usuário encontrado!")
        print(f"   ID: {usuario.id}")
        print(f"   Email: {usuario.email}")
        print(f"   Nome: {usuario.nome}")
        print(f"   Perfil: {usuario.perfil}")
        print(f"   Ativo: {usuario.ativo}")
        print(f"   Tentativas Login: {usuario.tentativas_login}")
        print(f"   Bloqueado até: {usuario.bloqueado_ate}")
        
        # 2. Verificar hash
        print("\n2️⃣  Verificando hash da senha...")
        print(f"   Tamanho do hash: {len(usuario.senha_hash)} caracteres")
        print(f"   Início do hash: {usuario.senha_hash[:20]}...")
        
        # Verificar se é bcrypt válido
        if usuario.senha_hash.startswith('$2b$') or usuario.senha_hash.startswith('$2a$'):
            print("   ✅ Hash bcrypt válido")
        else:
            print("   ⚠️  Hash não é bcrypt padrão!")
            print("   🔧 Será recriado...")
        
        # 3. Testar verificação de senha
        print("\n3️⃣  Testando verificação de senha...")
        print(f"   Senha teste: {senha_teste}")
        
        try:
            resultado = verify_password(senha_teste, usuario.senha_hash)
            print(f"   Resultado: {resultado}")
            
            if resultado:
                print("   ✅ Senha verificada com sucesso!")
            else:
                print("   ❌ Senha não confere!")
                print("   🔧 Recriando hash...")
                
                # Recriar hash
                novo_hash = hash_password(senha_teste)
                print(f"   Novo hash: {novo_hash[:20]}...")
                
                # Atualizar no banco
                usuario.senha_hash = novo_hash
                usuario.salt = generate_salt()
                usuario.tentativas_login = 0
                usuario.bloqueado_ate = None
                usuario.updated_at = datetime.utcnow()
                
                db.commit()
                
                print("   ✅ Hash atualizado no banco!")
                
                # Testar novamente
                print("\n4️⃣  Testando novamente...")
                resultado_novo = verify_password(senha_teste, novo_hash)
                print(f"   Resultado: {resultado_novo}")
                
                if resultado_novo:
                    print("   ✅ Senha agora funciona!")
                else:
                    print("   ❌ Ainda não funciona - problema mais profundo")
        
        except Exception as e:
            print(f"   ❌ Erro ao verificar senha: {e}")
            print("   🔧 Recriando hash do zero...")
            
            # Recriar hash do zero
            novo_hash = hash_password(senha_teste)
            usuario.senha_hash = novo_hash
            usuario.salt = generate_salt()
            usuario.tentativas_login = 0
            usuario.bloqueado_ate = None
            usuario.updated_at = datetime.utcnow()
            
            db.commit()
            print("   ✅ Hash recriado e atualizado!")
        
        # 5. Resumo final
        print("\n" + "=" * 70)
        print("📝 RESUMO FINAL")
        print("=" * 70)
        print(f"Email: {email}")
        print(f"Senha: {senha_teste}")
        print(f"Status: {'✅ PRONTO' if usuario.ativo else '❌ INATIVO'}")
        print(f"Tentativas: {usuario.tentativas_login}/5")
        print("=" * 70)
        print("\n🧪 Teste o login agora:")
        print(f'curl -X POST "http://localhost:8000/api/v1/auth/login" \\')
        print(f'  -H "Content-Type: application/json" \\')
        print(f'  -d \'{{"email": "{email}", "senha": "{senha_teste}"}}\'')
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    debug_login()