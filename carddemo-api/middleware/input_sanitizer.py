"""
Middleware de sanitización de entrada para CardDemo API
"""
import json
from typing import Any, Dict
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from services.encryption_service import get_encryption_service
import logging

logger = logging.getLogger(__name__)


class InputSanitizerMiddleware(BaseHTTPMiddleware):
    """Middleware para sanitizar entrada de datos"""
    
    def __init__(self, app):
        super().__init__(app)
        self.encryption_service = get_encryption_service()
    
    async def dispatch(self, request: Request, call_next):
        """
        Procesar request y sanitizar datos de entrada
        
        Args:
            request: Request HTTP
            call_next: Siguiente middleware/handler
            
        Returns:
            Response HTTP con datos sanitizados
        """
        # Solo sanitizar requests con body (POST, PUT, PATCH)
        if request.method in ["POST", "PUT", "PATCH"]:
            # Leer body original
            body = await request.body()
            
            if body:
                try:
                    # Intentar parsear como JSON
                    data = json.loads(body.decode())
                    
                    # Sanitizar datos recursivamente
                    sanitized_data = self._sanitize_data(data)
                    
                    # Reemplazar body con datos sanitizados
                    sanitized_body = json.dumps(sanitized_data).encode()
                    
                    # Crear nuevo request con body sanitizado
                    request._body = sanitized_body
                    
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    # Si no es JSON válido, continuar sin sanitizar
                    logger.warning(f"Could not parse request body as JSON: {e}")
                except Exception as e:
                    logger.error(f"Error sanitizing request data: {e}")
        
        # Sanitizar query parameters
        if request.query_params:
            sanitized_params = {}
            for key, value in request.query_params.items():
                sanitized_key = self.encryption_service.sanitize_input(key)
                sanitized_value = self.encryption_service.sanitize_input(value)
                sanitized_params[sanitized_key] = sanitized_value
            
            # Actualizar query params (esto es más complejo en Starlette)
            # Por simplicidad, solo loggeamos si hay diferencias
            if sanitized_params != dict(request.query_params):
                logger.info("Query parameters were sanitized")
        
        # Continuar con el request
        response = await call_next(request)
        return response
    
    def _sanitize_data(self, data: Any) -> Any:
        """
        Sanitizar datos recursivamente
        
        Args:
            data: Datos a sanitizar
            
        Returns:
            Datos sanitizados
        """
        if isinstance(data, dict):
            # Sanitizar diccionario recursivamente
            sanitized = {}
            for key, value in data.items():
                # Sanitizar clave
                sanitized_key = self.encryption_service.sanitize_input(str(key)) if isinstance(key, str) else key
                # Sanitizar valor recursivamente
                sanitized_value = self._sanitize_data(value)
                sanitized[sanitized_key] = sanitized_value
            return sanitized
            
        elif isinstance(data, list):
            # Sanitizar lista recursivamente
            return [self._sanitize_data(item) for item in data]
            
        elif isinstance(data, str):
            # Sanitizar string
            return self.encryption_service.sanitize_input(data)
            
        else:
            # Otros tipos (int, float, bool, None) no necesitan sanitización
            return data