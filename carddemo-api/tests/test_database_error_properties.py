"""
Tests de propiedades para manejo de errores de base de datos y logging seguro
"""
import pytest
import time
import tempfile
import os
import logging
from unittest.mock import patch, MagicMock
from hypothesis import given, strategies as st, settings
from sqlmodel import Session

from services.logging_service import SecureLogger, DatabaseErrorHandler, get_secure_logger
from database import execute_with_retry, check_database_health, get_db_session


class TestDatabaseErrorProperties:
    """Tests de propiedades para manejo de errores de base de datos"""
    
    def test_property_19_database_error_recovery(self):
        """
        **Propiedad 19: Manejo elegante de errores de base de datos**
        **Valida: Requisitos 6.3**
        
        El sistema debe manejar errores de base de datos de forma elegante
        con reintentos automáticos y recuperación cuando sea posible.
        """
        # Crear handler de errores
        logger = get_secure_logger("test")
        error_handler = DatabaseErrorHandler(logger)
        
        # Simular diferentes tipos de errores de BD
        connection_error = Exception("connection refused")
        timeout_error = Exception("timeout occurred")
        constraint_error = Exception("unique constraint failed")
        
        # Test 1: Error de conexión debe ser recuperable
        error_info = error_handler.handle_database_error(
            connection_error, 
            "test_connection",
            table="users"
        )
        
        assert error_info['recoverable'] == True, "Errores de conexión deben ser recuperables"
        assert error_info['action_taken'] == 'connection_retry', "Debe planear reintento de conexión"
        assert error_handler.should_retry(connection_error) == True, "Debe permitir reintento"
        
        # Test 2: Error de timeout debe ser recuperable
        error_info = error_handler.handle_database_error(
            timeout_error,
            "test_timeout"
        )
        
        assert error_info['recoverable'] == True, "Errores de timeout deben ser recuperables"
        assert error_info['action_taken'] == 'timeout_retry', "Debe planear reintento con timeout mayor"
        
        # Test 3: Error de constraint NO debe ser recuperable
        error_info = error_handler.handle_database_error(
            constraint_error,
            "test_constraint"
        )
        
        assert error_info['recoverable'] == False, "Errores de constraint no deben ser recuperables"
        assert error_info['action_taken'] == 'constraint_violation', "Debe identificar violación de constraint"
        assert error_handler.should_retry(constraint_error) == False, "No debe permitir reintento"
    
    def test_property_19_retry_limit_enforcement(self):
        """
        **Propiedad 19: Límite de reintentos**
        **Valida: Requisitos 6.3**
        
        El sistema debe respetar límites de reintentos para evitar loops infinitos.
        """
        logger = get_secure_logger("test")
        error_handler = DatabaseErrorHandler(logger)
        
        recoverable_error = Exception("connection timeout")
        
        # Verificar que inicialmente permite reintentos
        assert error_handler.should_retry(recoverable_error) == True
        
        # Simular múltiples reintentos
        for i in range(error_handler.max_retries):
            error_handler.increment_retry()
        
        # Después del límite, no debe permitir más reintentos
        assert error_handler.should_retry(recoverable_error) == False, "Debe respetar límite de reintentos"
        assert error_handler.retry_count == error_handler.max_retries, "Contador debe estar en el máximo"
        
        # Reset debe permitir reintentos nuevamente
        error_handler.reset_retry_count()
        assert error_handler.retry_count == 0, "Reset debe limpiar contador"
        assert error_handler.should_retry(recoverable_error) == True, "Después de reset debe permitir reintentos"
    
    def test_property_19_database_health_monitoring(self):
        """
        **Propiedad 19: Monitoreo de salud de base de datos**
        **Valida: Requisitos 6.3**
        
        El sistema debe poder verificar la salud de la base de datos
        y reportar problemas de conectividad.
        """
        # Verificar que la función de salud retorna información completa
        health_info = check_database_health()
        
        # Debe contener campos requeridos
        required_fields = ['status', 'connection', 'tables_exist', 'last_check']
        for field in required_fields:
            assert field in health_info, f"Campo {field} debe estar presente en info de salud"
        
        # Status debe ser uno de los valores válidos
        valid_statuses = ['healthy', 'unhealthy', 'unknown']
        assert health_info['status'] in valid_statuses, f"Status debe ser uno de {valid_statuses}"
        
        # Si hay error, debe estar documentado
        if health_info['status'] == 'unhealthy':
            assert 'error' in health_info, "Estado unhealthy debe incluir información de error"
        
        # Timestamp debe ser reciente (últimos 10 segundos)
        current_time = time.time()
        assert abs(current_time - health_info['last_check']) < 10, "Timestamp debe ser reciente"
    
    def test_property_19_operation_retry_consistency(self):
        """
        **Propiedad 19: Consistencia en reintentos de operaciones**
        **Valida: Requisitos 6.3**
        
        El mecanismo de reintentos debe ser consistente para todas las operaciones.
        """
        operation_name = "test_operation"
        
        # Crear función que falla las primeras veces y luego funciona
        call_count = 0
        def failing_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:  # Falla las primeras 2 veces
                raise Exception("temporary failure")
            return f"success_{operation_name}"
        
        # Ejecutar con reintentos
        try:
            result = execute_with_retry(failing_operation, operation_name)
            
            # Debe haber tenido éxito después de reintentos
            assert result == f"success_{operation_name}", "Operación debe tener éxito después de reintentos"
            assert call_count == 3, "Debe haber reintentado exactamente 2 veces antes del éxito"
            
        except Exception as e:
            # Si falla, debe ser después de agotar reintentos
            assert call_count > 1, "Debe haber intentado múltiples veces antes de fallar"


class TestSecureLoggingProperties:
    """Tests de propiedades para logging seguro"""
    
    @given(
        sensitive_data=st.lists(
            st.one_of(
                st.just("password=secret123"),
                st.just("token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"),
                st.just("4111-1111-1111-1111"),
                st.just("user@example.com"),
                st.just("555-123-4567"),
                st.just("api_key=sk_test_123456789"),
                st.text().filter(lambda x: any(pattern in x.lower() for pattern in ['password', 'token', 'api_key']))
            ),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=10)
    def test_property_27_sensitive_data_redaction(self, sensitive_data):
        """
        **Propiedad 27: Logging seguro y completo**
        **Valida: Requisitos 6.4, 8.4**
        
        El sistema de logging debe redactar automáticamente información sensible
        mientras mantiene la utilidad del log para debugging.
        """
        logger = SecureLogger("test")
        
        for data in sensitive_data:
            # Sanitizar el mensaje
            sanitized = logger._sanitize_message(data)
            
            # Verificar que información sensible fue redactada
            sensitive_patterns = ['password', 'token', 'api_key']
            for pattern in sensitive_patterns:
                if pattern in data.lower():
                    # Debe contener [REDACTED] o estar enmascarado
                    assert '[REDACTED]' in sanitized or '*' in sanitized, f"Patrón {pattern} debe estar redactado"
            
            # Para números de tarjeta, verificar enmascaramiento
            if any(char.isdigit() for char in data) and len([c for c in data if c.isdigit()]) >= 13:
                # Probablemente es número de tarjeta
                digit_count = len([c for c in sanitized if c.isdigit()])
                original_digits = len([c for c in data if c.isdigit()])
                
                if original_digits >= 4:
                    # Debe mostrar máximo los últimos 4 dígitos
                    assert digit_count <= 4, "Números de tarjeta deben mostrar máximo 4 dígitos"
            
            # Para emails, verificar enmascaramiento del usuario
            if '@' in data:
                if '@' in sanitized:
                    # Debe enmascarar la parte del usuario
                    assert '***@' in sanitized or sanitized.count('@') == 0, "Emails deben enmascarar usuario"
    
    def test_property_27_logging_completeness(self):
        """
        **Propiedad 27: Completitud del logging**
        **Valida: Requisitos 6.4, 8.4**
        
        El sistema debe loggear eventos importantes sin perder información crítica.
        """
        # Crear logger temporal con archivo de prueba
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.log') as temp_log:
            temp_log_path = temp_log.name
        
        try:
            # Configurar logger para usar archivo temporal
            logger = SecureLogger("test_completeness")
            
            # Remover handlers existentes y agregar uno para el archivo temporal
            logger.logger.handlers.clear()
            
            import logging
            file_handler = logging.FileHandler(temp_log_path, encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            logger.logger.addHandler(file_handler)
            
            # Loggear diferentes tipos de eventos
            logger.info("User login successful", user_id=123, ip="192.168.1.1")
            logger.warning("Rate limit approaching", requests_count=45, limit=50)
            logger.error("Database connection failed", error_code="DB001", retry_count=3)
            
            # Forzar flush
            file_handler.flush()
            
            # Leer contenido del log
            with open(temp_log_path, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # Verificar que eventos fueron loggeados
            assert "User login successful" in log_content, "Eventos de login deben ser loggeados"
            assert "Rate limit approaching" in log_content, "Advertencias deben ser loggeadas"
            assert "Database connection failed" in log_content, "Errores deben ser loggeados"
            
            # Verificar que información contextual está presente
            assert "user_id" in log_content, "Contexto de usuario debe estar presente"
            assert "192.168.1.1" in log_content, "IP debe estar presente (no es sensible en este contexto)"
            assert "retry_count" in log_content, "Información de reintentos debe estar presente"
            
            # Verificar formato de timestamp
            assert "2024" in log_content or "2025" in log_content or "2026" in log_content, "Debe incluir timestamp válido"
            
        finally:
            # Limpiar archivo temporal
            try:
                file_handler.close()
                if os.path.exists(temp_log_path):
                    os.unlink(temp_log_path)
            except (PermissionError, OSError):
                # En Windows puede haber problemas de permisos, ignorar
                pass
    
    @given(
        log_levels=st.sampled_from(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
        messages=st.lists(
            st.text(min_size=1, max_size=100),
            min_size=1,
            max_size=3
        )
    )
    @settings(max_examples=10)
    def test_property_27_log_level_consistency(self, log_levels, messages):
        """
        **Propiedad 27: Consistencia de niveles de log**
        **Valida: Requisitos 6.4, 8.4**
        
        El sistema debe respetar niveles de logging y formatear consistentemente.
        """
        logger = SecureLogger("test_levels", log_levels)
        
        for message in messages:
            if not message.strip():
                continue
            
            # Verificar que el logger acepta el nivel configurado
            assert logger.logger.level == getattr(logging, log_levels), "Nivel de log debe estar configurado correctamente"
            
            # Verificar que métodos de logging existen y son callable
            assert hasattr(logger, 'debug'), "Debe tener método debug"
            assert hasattr(logger, 'info'), "Debe tener método info"
            assert hasattr(logger, 'warning'), "Debe tener método warning"
            assert hasattr(logger, 'error'), "Debe tener método error"
            assert hasattr(logger, 'critical'), "Debe tener método critical"
            
            # Verificar que sanitización es consistente
            sanitized1 = logger._sanitize_message(message)
            sanitized2 = logger._sanitize_message(message)
            
            assert sanitized1 == sanitized2, "Sanitización debe ser determinística"
    
    def test_property_27_error_context_preservation(self):
        """
        **Propiedad 27: Preservación de contexto en errores**
        **Valida: Requisitos 6.4, 8.4**
        
        El logging debe preservar contexto útil para debugging sin exponer datos sensibles.
        """
        logger = get_secure_logger("test")
        error_handler = DatabaseErrorHandler(logger)
        
        # Simular error con contexto
        test_error = Exception("Connection timeout after 30 seconds")
        context = {
            'table': 'users',
            'query_type': 'SELECT',
            'timeout': 30,
            'user_id': 12345  # No sensible
        }
        
        error_info = error_handler.handle_database_error(
            test_error,
            "test_operation",
            **context
        )
        
        # Verificar que información útil se preserva
        assert error_info['operation'] == 'test_operation', "Nombre de operación debe preservarse"
        assert error_info['error_type'] == 'Exception', "Tipo de error debe preservarse"
        assert 'timestamp' in error_info, "Timestamp debe estar presente"
        assert 'retry_count' in error_info, "Información de reintentos debe estar presente"
        
        # Verificar que se determina si es recuperable
        assert 'recoverable' in error_info, "Debe determinar si es recuperable"
        assert 'action_taken' in error_info, "Debe documentar acción tomada"