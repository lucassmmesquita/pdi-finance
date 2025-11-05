"""
PDI Finance - API Router Aggregator
Centraliza todos os endpoints da API
"""
from fastapi import APIRouter

# Importa o router de autenticação existente
from app.api.v1.endpoints.auth import router as auth_router

# Importa os novos routers de gestão
from app.api.executoras import router as executoras_router
from app.api.projetos import router as projetos_router

# Criar router principal da API (sem prefix aqui, será adicionado no main.py)
api_router = APIRouter()

# ==========================================
# ROTAS DE AUTENTICAÇÃO (já existentes)
# ==========================================
api_router.include_router(
    auth_router,
    tags=["Autenticação"]
)

# ==========================================
# ROTAS DE GESTÃO DE PROJETOS (novas)
# ==========================================
api_router.include_router(
    executoras_router,
    tags=["Executoras"]
)

api_router.include_router(
    projetos_router,
    tags=["Projetos"]
)

# ==========================================
# PRÓXIMAS ROTAS (a serem implementadas)
# ==========================================
# from app.api.incisos import router as incisos_router
# api_router.include_router(incisos_router, tags=["Incisos"])

# from app.api.rh import router as rh_router
# api_router.include_router(rh_router, tags=["Recursos Humanos"])

# from app.api.aportes import router as aportes_router
# api_router.include_router(aportes_router, tags=["Aportes"])

# from app.api.despesas import router as despesas_router
# api_router.include_router(despesas_router, tags=["Despesas"])

# from app.api.relatorios import router as relatorios_router
# api_router.include_router(relatorios_router, tags=["Relatórios"])

# from app.api.importacao import router as importacao_router
# api_router.include_router(importacao_router, tags=["Importação"])