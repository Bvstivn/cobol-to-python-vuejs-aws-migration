"""
CardDemo API - Aplicación principal FastAPI
Migración de la aplicación mainframe CardDemo COBOL a API REST moderna
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routers import auth
from middleware import ErrorHandlerMiddleware, RateLimitMiddleware, InputSanitizerMiddleware, setup_logging, setup_exception_handlers
from database import init_database

# Configurar logging
setup_logging()

# Inicializar base de datos
init_database()

# Crear instancia de FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API REST para gestión de tarjetas de crédito - Migración de CardDemo COBOL",
    debug=settings.debug
)

# Agregar middleware de sanitización de entrada (debe ser el primero)
app.add_middleware(InputSanitizerMiddleware)

# Agregar middleware de rate limiting con configuración más permisiva para tests
import os
if os.getenv("TESTING"):
    # Configuración muy permisiva para tests
    app.add_middleware(RateLimitMiddleware, calls_per_minute=10000, calls_per_hour=100000, burst_limit=1000)
else:
    # Configuración normal para producción
    app.add_middleware(RateLimitMiddleware, calls_per_minute=60, calls_per_hour=1000, burst_limit=10)

# Agregar middleware de manejo de errores
app.add_middleware(ErrorHandlerMiddleware)

# Configurar exception handlers
setup_exception_handlers(app)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)

# Importar y incluir router de cuentas
from routers import accounts
app.include_router(accounts.router)

# Importar y incluir router de tarjetas
from routers import cards
app.include_router(cards.router)

# Importar y incluir router de transacciones
from routers import transactions
app.include_router(transactions.router)

# Importar y incluir router de salud
from routers import health
app.include_router(health.router)


@app.get("/")
async def root():
    """Endpoint raíz de la API"""
    return {
        "message": f"Bienvenido a {settings.app_name}",
        "version": settings.app_version,
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )