"""
PDI Finance - Main Application
Entry point da aplicação FastAPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import api_router
from app.core.config import settings
from app.api.v1.endpoints import auth


# ==========================================
# CRIAR APLICAÇÃO FASTAPI
# ==========================================

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)


# ==========================================
# CONFIGURAR CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# INCLUIR ROUTERS
# ==========================================

# Router de autenticação

app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX  # "/api/v1"
)

# ==========================================
# ENDPOINTS RAIZ
# ==========================================

@app.get("/")
def read_root():
    """
    Endpoint raiz - informações básicas da API
    """
    return {
        "message": "PDI Finance API",
        "version": settings.VERSION,
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    """
    Health check - verifica se API está funcionando
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


# ==========================================
# TRATAMENTO DE ERROS GLOBAL
# ==========================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Handler global para exceções não tratadas
    """
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor",
            "type": type(exc).__name__,
            "message": str(exc) if settings.DEBUG else "Erro interno"
        }
    )


# ==========================================
# STARTUP E SHUTDOWN EVENTS
# ==========================================

@app.on_event("startup")
async def startup_event():
    """
    Executado ao iniciar a aplicação
    """
    print("=" * 50)
    print(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"📝 Environment: {settings.ENVIRONMENT}")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print(f"🔐 Authentication: JWT")
    print("=" * 50)
    
    # Testar conexão com banco de dados
    from app.db.session import test_connection
    if test_connection():
        print("✅ Conexão com banco de dados OK")
    else:
        print("❌ Erro ao conectar ao banco de dados")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Executado ao desligar a aplicação
    """
    print("\n" + "=" * 50)
    print("🛑 Desligando PDI Finance API...")
    print("=" * 50)


# ==========================================
# EXECUTAR APLICAÇÃO
# ==========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False
    )