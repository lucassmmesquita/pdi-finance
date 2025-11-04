# 💰 PDI Finance

Sistema de Controle Orçamentário e Financeiro de Projetos PD&I

## 🚀 Tecnologias

- **Backend**: Python 3.11 + FastAPI
- **Frontend**: React 18 + Vite + Tailwind CSS
- **Banco de Dados**: PostgreSQL 15
- **ORM**: SQLAlchemy

## 📋 Pré-requisitos

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Git

## 🔧 Instalação

### 1. Clone o repositório
```bash
git clone <url-do-repo>
cd pdi-finance
```

### 2. Configure o Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edite o .env com suas configurações
```

### 3. Configure o Frontend
```bash
cd frontend
npm install
cp .env.example .env
```

### 4. Configure o Banco de Dados
```bash
# Crie o banco e execute o schema
psql -U postgres
CREATE DATABASE pdi_finance;
\q

psql -U postgres -d pdi_finance -f database/migrations/001_initial_schema.sql
```

### 5. Execute o projeto
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Acesse: http://localhost:5173

## 📚 Documentação

- API Docs: http://localhost:8000/docs
- User Guide: /docs/user-guide/

## 👤 Login Padrão

- Email: `admin@pdifinance.com`
- Senha: `Admin@2025`

**⚠️ Altere a senha no primeiro login!**

## 📝 Licença

Propriedade do Grupo IREDE
