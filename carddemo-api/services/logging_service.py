"""
Servicio de logging seguro para CardDemo API
"""
import logging
import json
import re
from typing import Any, Dict, Optional
from datetime import datetime, timezone
from pathlib import Path
import os


class SecureLogger:
    """Logger que excluye información sensible automáticamente"""
    
    # Patrones de datos sensibles que deben ser enmascarados
    SENSITIVE_PATTERNS = {
        'password': re.compile(r'(password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', re.IGNORECASE),
        'token': re.compile(r'(token|jwt|bearer)["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', re.IGNORECASE),
        'card_number': re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
        'ssn': re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b'),
        'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        'phone': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
        'api_key': re.compile(r'(api[_-]?key|apikey)["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', re.IGNORECASE),
    }
    
    def __init__(self, name: str, log_level: str = "INFO"):
        """
        Inicializar logger seguro
        
        Args:
            name: Nombre del logger
            log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Configurar handler si no existe
        if not self.logger.handlers:
            self._setup_handler()
    
    def _setup_handler(self):
        """Configurar handler de logging con formato seguro"""
        # Crear directorio de logs si no existe
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Handler para archivo
        file_handler = logging.FileHandler(
            log_dir / "carddemo-api.log",
            encoding='utf-8'
        )
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        
        # Formato de log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _sanitize_message(self, message: str) -> str:
        """
        Sanitizar mensaje removiendo información sensible
        
        Args:
            message: Mensaje original
            
        Returns:
            Mensaje sanitizado
        """
        sanitized = message
        
        for pattern_name, pattern in self.SENSITIVE_PATTERNS.items():
            if pattern_name in ['password', 'token', 'api_key']:
                # Para campos con valores, reemplazar el valor
                sanitized = pattern.sub(r'\1: [REDACTED]', sanitized)
            elif pattern_name == 'card_number':
                # Para números de tarjeta, mostrar solo últimos 4 dígitos
                def mask_card(match):
                    card = match.group(0)
                    clean_card = re.sub(r'[\s-]', '', card)
                    if len(clean_card) >= 4:
                        return '*' * (len(clean_card) - 4) + clean_card[-4:]
                    return '*' * len(clean_card)
                sanitized = pattern.sub(mask_card, sanitized)
            elif pattern_name == 'email':
                # Para emails, mostrar solo dominio
                def mask_email(match):
                    email = match.group(0)
                    if '@' in email:
                        local, domain = email.split('@', 1)
                        return f"***@{domain}"
                    return "***@***.***"
                sanitized = pattern.sub(mask_email, sanitized)
            elif pattern_name in ['ssn', 'phone']:
                # Para SSN y teléfonos, enmascarar completamente
                sanitized = pattern.sub('[REDACTED]', sanitized)
        
        return sanitized
    
    def _format_extra_data(self, **kwargs) -> str:
        """
        Formatear datos extra de forma segura
        
        Args:
            **kwargs: Datos adicionales
            
        Returns:
            String formateado y sanitizado
        """
        if not kwargs:
            return ""
        
        try:
            # Convertir a JSON y sanitizar
            json_str = json.dumps(kwargs, default=str, ensure_ascii=False)
            sanitized = self._sanitize_message(json_str)
            return f" | Extra: {sanitized}"
        except Exception:
            return f" | Extra: [Error formatting data]"
    
    def debug(self, message: str, **kwargs):
        """Log mensaje de debug"""
        sanitized_msg = self._sanitize_message(str(message))
        extra_data = self._format_extra_data(**kwargs)
        self.logger.debug(f"{sanitized_msg}{extra_data}")
    
    def info(self, message: str, **kwargs):
        """Log mensaje informativo"""
        sanitized_msg = self._sanitize_message(str(message))
        extra_data = self._format_extra_data(**kwargs)
        self.logger.info(f"{sanitized_msg}{extra_data}")
    
    def warning(self, message: str, **kwargs):
        """Log mensaje de advertencia"""
        sanitized_msg = self._sanitize_message(str(message))
        extra_data = self._format_extra_data(**kwargs)
        self.logger.warning(f"{sanitized_msg}{extra_data}")
    
    def error(self, message: str, **kwargs):
        """Log mensaje de error"""
        sanitized_msg = self._sanitize_message(str(message))
        extra_data = self._format_extra_data(**kwargs)
        self.logger.error(f"{sanitized_msg}{extra_data}")
    
    def critical(self, message: str, **kwargs):
        """Log mensaje crítico"""
        sanitized_msg = self._sanitize_message(str(message))
        extra_data = self._format_extra_data(**kwargs)
        self.logger.critical(f"{sanitized_msg}{extra_data}")


class DatabaseErrorHandler:
    """Manejador de errores de base de datos con recuperación automática"""
    
    def __init__(self, logger: SecureLogger):
        """
        Inicializar manejador de errores de BD
        
        Args:
            logger: Logger seguro para registrar errores
        """
        self.logger = logger
        self.retry_count = 0
        self.max_retries = 3
        self.retry_delay = 1.0  # segundos
    
    def handle_database_error(self, error: Exception, operation: str, **context) -> Dict[str, Any]:
        """
        Manejar error de base de datos con recuperación
        
        Args:
            error: Excepción de base de datos
            operation: Descripción de la operación que falló
            **context: Contexto adicional (sin datos sensibles)
            
        Returns:
            Diccionario con información del error y acciones tomadas
        """
        error_info = {
            'error_type': type(error).__name__,
            'operation': operation,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'retry_count': self.retry_count,
            'recoverable': self._is_recoverable_error(error),
            'action_taken': None
        }
        
        # Log del error (sin información sensible)
        self.logger.error(
            f"Database error in {operation}: {str(error)}",
            error_type=error_info['error_type'],
            retry_count=self.retry_count,
            **context
        )
        
        # Determinar acción basada en el tipo de error
        if self._is_timeout_error(error):
            error_info['action_taken'] = 'timeout_retry'
            self.logger.warning(f"Timeout error detected, will retry with longer timeout: {operation}")
            
        elif self._is_connection_error(error):
            error_info['action_taken'] = 'connection_retry'
            self.logger.warning(f"Connection error detected, will retry operation: {operation}")
            
        elif self._is_constraint_error(error):
            error_info['action_taken'] = 'constraint_violation'
            self.logger.error(f"Constraint violation in {operation}, operation cannot be retried")
            
        elif self._is_integrity_error(error):
            error_info['action_taken'] = 'integrity_violation'
            self.logger.error(f"Data integrity error in {operation}, manual intervention required")
            
        else:
            error_info['action_taken'] = 'unknown_error'
            self.logger.critical(f"Unknown database error in {operation}: {str(error)}")
        
        return error_info
    
    def _is_recoverable_error(self, error: Exception) -> bool:
        """
        Determinar si el error es recuperable con reintento
        
        Args:
            error: Excepción de base de datos
            
        Returns:
            True si el error es recuperable
        """
        recoverable_errors = [
            'OperationalError',  # Errores de conexión, timeouts
            'DisconnectionError',  # Desconexiones
            'TimeoutError',  # Timeouts
            'DatabaseError'  # Errores generales de BD que pueden ser temporales
        ]
        
        error_name = type(error).__name__
        error_str = str(error).lower()
        
        # Verificar por nombre de clase
        if error_name in recoverable_errors:
            return True
        
        # Verificar por contenido del mensaje para errores genéricos
        recoverable_indicators = [
            'connection', 'timeout', 'network', 'temporary', 'retry'
        ]
        
        return any(indicator in error_str for indicator in recoverable_indicators)
    
    def _is_connection_error(self, error: Exception) -> bool:
        """Verificar si es error de conexión"""
        error_str = str(error).lower()
        connection_indicators = [
            'connection', 'connect', 'network', 'host', 'server',
            'unreachable', 'refused'
        ]
        # Excluir timeout ya que tiene su propia categoría
        if 'timeout' in error_str or 'time out' in error_str:
            return False
        return any(indicator in error_str for indicator in connection_indicators)
    
    def _is_timeout_error(self, error: Exception) -> bool:
        """Verificar si es error de timeout"""
        error_str = str(error).lower()
        return 'timeout' in error_str or 'time out' in error_str
    
    def _is_constraint_error(self, error: Exception) -> bool:
        """Verificar si es error de constraint"""
        error_str = str(error).lower()
        constraint_indicators = [
            'constraint', 'unique', 'foreign key', 'check constraint',
            'not null', 'primary key'
        ]
        return any(indicator in error_str for indicator in constraint_indicators)
    
    def _is_integrity_error(self, error: Exception) -> bool:
        """Verificar si es error de integridad de datos"""
        error_name = type(error).__name__
        return error_name in ['IntegrityError', 'DataError']
    
    def should_retry(self, error: Exception) -> bool:
        """
        Determinar si se debe reintentar la operación
        
        Args:
            error: Excepción de base de datos
            
        Returns:
            True si se debe reintentar
        """
        if self.retry_count >= self.max_retries:
            return False
        
        return self._is_recoverable_error(error)
    
    def increment_retry(self):
        """Incrementar contador de reintentos"""
        self.retry_count += 1
    
    def reset_retry_count(self):
        """Resetear contador de reintentos"""
        self.retry_count = 0


# Instancias globales
_secure_logger = None
_db_error_handler = None


def get_secure_logger(name: str = "carddemo-api") -> SecureLogger:
    """
    Obtener instancia global del logger seguro
    
    Args:
        name: Nombre del logger
        
    Returns:
        Instancia de SecureLogger
    """
    global _secure_logger
    if _secure_logger is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")
        _secure_logger = SecureLogger(name, log_level)
    return _secure_logger


def get_db_error_handler() -> DatabaseErrorHandler:
    """
    Obtener instancia global del manejador de errores de BD
    
    Returns:
        Instancia de DatabaseErrorHandler
    """
    global _db_error_handler
    if _db_error_handler is None:
        logger = get_secure_logger("database")
        _db_error_handler = DatabaseErrorHandler(logger)
    return _db_error_handler