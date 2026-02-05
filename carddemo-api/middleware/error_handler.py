"""
Middleware de manejo de errores global para CardDemo API
"""
import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import Request, Response, HTTPException, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError


# Configurar logger
logger = logging.getLogger("carddemo.errors")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware para manejo global de errores"""
    
    async def dispatch(self, request: Request, call_next):
        """
        Procesar request y manejar errores de manera consistente
        
        Args:
            request: Request HTTP
            call_next: Siguiente middleware/handler
            
        Returns:
            Response HTTP con manejo de errores estandarizado
        """
        # Generar correlation ID único para esta request
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        try:
            # Procesar request
            response = await call_next(request)
            
            # Agregar correlation ID a headers de respuesta exitosa
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except SQLAlchemyError as e:
            # Error de base de datos
            logger.error(
                f"Database error - Correlation ID: {correlation_id}",
                extra={
                    "correlation_id": correlation_id,
                    "path": request.url.path,
                    "method": request.method,
                    "error": str(e)
                },
                exc_info=True
            )
            
            return self._create_error_response(
                status_code=500,
                error_code="DATABASE_ERROR",
                message="Error interno del servidor - problema de base de datos",
                correlation_id=correlation_id,
                request=request
            )
            
        except Exception as e:
            # Error genérico no manejado (excluyendo HTTPException que maneja FastAPI)
            if isinstance(e, HTTPException):
                # Re-raise HTTPException para que FastAPI la maneje
                raise e
                
            logger.error(
                f"Unhandled error - Correlation ID: {correlation_id}",
                extra={
                    "correlation_id": correlation_id,
                    "path": request.url.path,
                    "method": request.method,
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                exc_info=True
            )
            
            return self._create_error_response(
                status_code=500,
                error_code="INTERNAL_SERVER_ERROR",
                message="Error interno del servidor",
                correlation_id=correlation_id,
                request=request
            )
    
    def _create_error_response(
        self,
        status_code: int,
        error_code: str,
        message: str,
        correlation_id: str,
        request: Request,
        details: Optional[list] = None
    ) -> JSONResponse:
        """
        Crear respuesta de error estandarizada
        
        Args:
            status_code: Código de estado HTTP
            error_code: Código de error interno
            message: Mensaje de error
            correlation_id: ID de correlación
            request: Request HTTP
            details: Detalles adicionales del error
            
        Returns:
            JSONResponse con formato de error estandarizado
        """
        error_response = {
            "error": {
                "code": error_code,
                "message": message,
                "correlation_id": correlation_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "path": request.url.path,
                "method": request.method
            }
        }
        
        if details:
            error_response["error"]["details"] = details
        
        return JSONResponse(
            status_code=status_code,
            content=error_response,
            headers={"X-Correlation-ID": correlation_id}
        )
    
    def _format_validation_errors(self, errors: list) -> list:
        """
        Formatear errores de validación de Pydantic
        
        Args:
            errors: Lista de errores de Pydantic
            
        Returns:
            Lista de errores formateados
        """
        formatted_errors = []
        
        for error in errors:
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            formatted_errors.append({
                "field": field_path,
                "message": error["msg"],
                "type": error["type"]
            })
        
        return formatted_errors


def setup_logging():
    """Configurar logging para la aplicación"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configurar logger específico para errores
    error_logger = logging.getLogger("carddemo.errors")
    error_logger.setLevel(logging.INFO)
    
    # En producción, aquí se configurarían handlers específicos
    # como archivos de log, servicios de logging, etc.
    
    return error_logger


def setup_exception_handlers(app: FastAPI):
    """
    Configurar exception handlers para FastAPI
    
    Args:
        app: Instancia de FastAPI
    """
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handler para HTTPException"""
        correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
        
        logger.warning(
            f"HTTP Exception - Correlation ID: {correlation_id}",
            extra={
                "correlation_id": correlation_id,
                "path": request.url.path,
                "method": request.method,
                "status_code": exc.status_code,
                "detail": exc.detail
            }
        )
        
        error_response = {
            "error": {
                "code": "HTTP_EXCEPTION",
                "message": exc.detail,
                "correlation_id": correlation_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "path": request.url.path,
                "method": request.method
            }
        }
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
            headers={"X-Correlation-ID": correlation_id}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handler para errores de validación de FastAPI"""
        correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
        
        logger.warning(
            f"Validation error - Correlation ID: {correlation_id}",
            extra={
                "correlation_id": correlation_id,
                "path": request.url.path,
                "method": request.method,
                "validation_errors": exc.errors()
            }
        )
        
        # Formatear errores de validación
        formatted_errors = []
        for error in exc.errors():
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            formatted_errors.append({
                "field": field_path,
                "message": error["msg"],
                "type": error["type"]
            })
        
        error_response = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Los datos proporcionados no son válidos",
                "details": formatted_errors,
                "correlation_id": correlation_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "path": request.url.path,
                "method": request.method
            }
        }
        
        return JSONResponse(
            status_code=422,
            content=error_response,
            headers={"X-Correlation-ID": correlation_id}
        )


# Funciones de utilidad para obtener correlation ID
def get_correlation_id(request: Request) -> Optional[str]:
    """
    Obtener correlation ID de la request actual
    
    Args:
        request: Request HTTP
        
    Returns:
        Correlation ID si existe, None en caso contrario
    """
    return getattr(request.state, 'correlation_id', None)


def log_with_correlation(
    logger: logging.Logger,
    level: str,
    message: str,
    request: Request,
    **kwargs
):
    """
    Log con correlation ID automático
    
    Args:
        logger: Logger a usar
        level: Nivel de log (info, warning, error)
        message: Mensaje a loggear
        request: Request HTTP
        **kwargs: Argumentos adicionales para el logger
    """
    correlation_id = get_correlation_id(request)
    extra = kwargs.get('extra', {})
    extra['correlation_id'] = correlation_id
    kwargs['extra'] = extra
    
    log_method = getattr(logger, level.lower())
    log_method(f"{message} - Correlation ID: {correlation_id}", **kwargs)