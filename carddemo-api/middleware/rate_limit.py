"""
Middleware de rate limiting para CardDemo API
"""
import time
from typing import Dict, Optional
from collections import defaultdict, deque
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware para implementar rate limiting por IP y endpoint"""
    
    def __init__(
        self,
        app,
        calls_per_minute: int = 60,
        calls_per_hour: int = 1000,
        burst_limit: int = 10,
        cleanup_interval: int = 300  # 5 minutos
    ):
        """
        Inicializar middleware de rate limiting
        
        Args:
            app: Aplicación FastAPI
            calls_per_minute: Límite de llamadas por minuto por IP
            calls_per_hour: Límite de llamadas por hora por IP
            burst_limit: Límite de ráfaga (llamadas consecutivas rápidas)
            cleanup_interval: Intervalo de limpieza de datos antiguos en segundos
        """
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.calls_per_hour = calls_per_hour
        self.burst_limit = burst_limit
        self.cleanup_interval = cleanup_interval
        
        # Almacenamiento en memoria para tracking de requests
        # En producción, esto debería usar Redis o similar
        self.minute_requests: Dict[str, deque] = defaultdict(deque)
        self.hour_requests: Dict[str, deque] = defaultdict(deque)
        self.burst_requests: Dict[str, deque] = defaultdict(deque)
        
        # Timestamp de última limpieza
        self.last_cleanup = time.time()
    
    async def dispatch(self, request: Request, call_next):
        """
        Procesar request y aplicar rate limiting
        
        Args:
            request: Request HTTP
            call_next: Siguiente middleware/handler
            
        Returns:
            Response HTTP o error de rate limit
        """
        # Obtener IP del cliente
        client_ip = self._get_client_ip(request)
        
        # Limpiar datos antiguos periódicamente
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_requests(current_time)
            self.last_cleanup = current_time
        
        # Verificar límites
        if self._is_rate_limited(client_ip, request.url.path, current_time):
            return self._create_rate_limit_response(client_ip, request)
        
        # Registrar request
        self._record_request(client_ip, current_time)
        
        # Procesar request normalmente
        response = await call_next(request)
        
        # Agregar headers de rate limit info
        self._add_rate_limit_headers(response, client_ip, current_time)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Obtener IP del cliente considerando proxies
        
        Args:
            request: Request HTTP
            
        Returns:
            IP del cliente
        """
        # Verificar headers de proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Tomar la primera IP (cliente original)
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback a IP directa
        return request.client.host if request.client else "unknown"
    
    def _is_rate_limited(self, client_ip: str, path: str, current_time: float) -> bool:
        """
        Verificar si el cliente ha excedido los límites
        
        Args:
            client_ip: IP del cliente
            path: Ruta del endpoint
            current_time: Timestamp actual
            
        Returns:
            True si está limitado, False en caso contrario
        """
        # Verificar límite de ráfaga (últimos 10 segundos)
        burst_key = f"{client_ip}:burst"
        burst_requests = self.burst_requests[burst_key]
        
        # Limpiar requests antiguos de ráfaga
        while burst_requests and current_time - burst_requests[0] > 10:
            burst_requests.popleft()
        
        if len(burst_requests) >= self.burst_limit:
            logger.warning(f"Burst limit exceeded for IP {client_ip}")
            return True
        
        # Verificar límite por minuto
        minute_key = f"{client_ip}:minute"
        minute_requests = self.minute_requests[minute_key]
        
        # Limpiar requests antiguos del minuto
        while minute_requests and current_time - minute_requests[0] > 60:
            minute_requests.popleft()
        
        if len(minute_requests) >= self.calls_per_minute:
            logger.warning(f"Per-minute limit exceeded for IP {client_ip}")
            return True
        
        # Verificar límite por hora
        hour_key = f"{client_ip}:hour"
        hour_requests = self.hour_requests[hour_key]
        
        # Limpiar requests antiguos de la hora
        while hour_requests and current_time - hour_requests[0] > 3600:
            hour_requests.popleft()
        
        if len(hour_requests) >= self.calls_per_hour:
            logger.warning(f"Per-hour limit exceeded for IP {client_ip}")
            return True
        
        # Límites especiales para endpoints sensibles
        if self._is_sensitive_endpoint(path):
            # Límite más estricto para endpoints de autenticación
            auth_limit = min(10, self.calls_per_minute // 6)  # Máximo 10 por minuto
            if len(minute_requests) >= auth_limit:
                logger.warning(f"Auth endpoint limit exceeded for IP {client_ip} on {path}")
                return True
        
        return False
    
    def _is_sensitive_endpoint(self, path: str) -> bool:
        """
        Verificar si el endpoint es sensible y requiere límites más estrictos
        
        Args:
            path: Ruta del endpoint
            
        Returns:
            True si es endpoint sensible
        """
        sensitive_patterns = [
            '/auth/login',
            '/auth/logout',
            '/auth/me',
        ]
        
        return any(pattern in path for pattern in sensitive_patterns)
    
    def _record_request(self, client_ip: str, current_time: float):
        """
        Registrar request para tracking
        
        Args:
            client_ip: IP del cliente
            current_time: Timestamp actual
        """
        # Registrar en todas las ventanas de tiempo
        self.burst_requests[f"{client_ip}:burst"].append(current_time)
        self.minute_requests[f"{client_ip}:minute"].append(current_time)
        self.hour_requests[f"{client_ip}:hour"].append(current_time)
    
    def _cleanup_old_requests(self, current_time: float):
        """
        Limpiar requests antiguos para liberar memoria
        
        Args:
            current_time: Timestamp actual
        """
        # Limpiar requests de ráfaga (> 10 segundos)
        for key in list(self.burst_requests.keys()):
            requests = self.burst_requests[key]
            while requests and current_time - requests[0] > 10:
                requests.popleft()
            if not requests:
                del self.burst_requests[key]
        
        # Limpiar requests por minuto (> 60 segundos)
        for key in list(self.minute_requests.keys()):
            requests = self.minute_requests[key]
            while requests and current_time - requests[0] > 60:
                requests.popleft()
            if not requests:
                del self.minute_requests[key]
        
        # Limpiar requests por hora (> 3600 segundos)
        for key in list(self.hour_requests.keys()):
            requests = self.hour_requests[key]
            while requests and current_time - requests[0] > 3600:
                requests.popleft()
            if not requests:
                del self.hour_requests[key]
    
    def _create_rate_limit_response(self, client_ip: str, request: Request) -> JSONResponse:
        """
        Crear respuesta de rate limit excedido
        
        Args:
            client_ip: IP del cliente
            request: Request HTTP
            
        Returns:
            JSONResponse con error 429
        """
        correlation_id = getattr(request.state, 'correlation_id', 'unknown')
        
        error_response = {
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Demasiadas solicitudes. Intente nuevamente más tarde.",
                "correlation_id": correlation_id,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "path": request.url.path,
                "method": request.method
            }
        }
        
        headers = {
            "X-Correlation-ID": correlation_id,
            "Retry-After": "60"  # Sugerir reintentar en 60 segundos
        }
        
        return JSONResponse(
            status_code=429,
            content=error_response,
            headers=headers
        )
    
    def _add_rate_limit_headers(self, response, client_ip: str, current_time: float):
        """
        Agregar headers informativos sobre rate limiting
        
        Args:
            response: Response HTTP
            client_ip: IP del cliente
            current_time: Timestamp actual
        """
        # Calcular requests restantes
        minute_requests = len(self.minute_requests.get(f"{client_ip}:minute", []))
        hour_requests = len(self.hour_requests.get(f"{client_ip}:hour", []))
        
        remaining_minute = max(0, self.calls_per_minute - minute_requests)
        remaining_hour = max(0, self.calls_per_hour - hour_requests)
        
        # Agregar headers informativos
        response.headers["X-RateLimit-Limit-Minute"] = str(self.calls_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(remaining_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.calls_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(remaining_hour)
        
        # Tiempo hasta reset (próximo minuto)
        reset_time = int(current_time) + (60 - int(current_time) % 60)
        response.headers["X-RateLimit-Reset"] = str(reset_time)