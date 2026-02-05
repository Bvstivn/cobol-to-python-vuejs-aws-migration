"""
Tests para el middleware de manejo de errores
"""
import pytest
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import patch, MagicMock

from middleware.error_handler import ErrorHandlerMiddleware, setup_exception_handlers, get_correlation_id, log_with_correlation


# Crear app de prueba
test_app = FastAPI()
test_app.add_middleware(ErrorHandlerMiddleware)
setup_exception_handlers(test_app)


# Modelos de prueba
class TestRequestModel(BaseModel):
    name: str
    age: int


# Endpoints de prueba
@test_app.get("/test/success")
async def test_success_endpoint():
    return {"message": "success"}


@test_app.get("/test/http-exception")
async def test_http_exception_endpoint():
    raise HTTPException(status_code=404, detail="Not found")


@test_app.post("/test/validation-error")
async def test_validation_error_endpoint(data: TestRequestModel):
    return {"data": data}


@test_app.get("/test/database-error")
async def test_database_error_endpoint():
    raise SQLAlchemyError("Database connection failed")


@test_app.get("/test/generic-error")
async def test_generic_error_endpoint():
    raise ValueError("Something went wrong")


@test_app.get("/test/correlation-id")
async def test_correlation_id_endpoint(request: Request):
    correlation_id = get_correlation_id(request)
    return {"correlation_id": correlation_id}


client = TestClient(test_app)


class TestErrorHandlerMiddleware:
    """Tests para ErrorHandlerMiddleware"""
    
    def test_successful_request_adds_correlation_id(self):
        """Test que request exitosa agrega correlation ID"""
        response = client.get("/test/success")
        
        assert response.status_code == 200
        assert "X-Correlation-ID" in response.headers
        assert response.json() == {"message": "success"}
    
    def test_http_exception_handling(self):
        """Test manejo de HTTPException"""
        response = client.get("/test/http-exception")
        
        assert response.status_code == 404
        assert "X-Correlation-ID" in response.headers
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "HTTP_EXCEPTION"
        assert data["error"]["message"] == "Not found"
        assert "correlation_id" in data["error"]
        assert "timestamp" in data["error"]
        assert data["error"]["path"] == "/test/http-exception"
        assert data["error"]["method"] == "GET"
    
    def test_validation_error_handling(self):
        """Test manejo de errores de validación"""
        # Enviar datos inválidos
        response = client.post("/test/validation-error", json={"name": "test"})  # falta age
        
        assert response.status_code == 422
        assert "X-Correlation-ID" in response.headers
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert data["error"]["message"] == "Los datos proporcionados no son válidos"
        assert "details" in data["error"]
        assert len(data["error"]["details"]) > 0
        
        # Verificar formato de detalles de validación
        detail = data["error"]["details"][0]
        assert "field" in detail
        assert "message" in detail
        assert "type" in detail
    
    def test_database_error_handling(self):
        """Test manejo de errores de base de datos"""
        response = client.get("/test/database-error")
        
        assert response.status_code == 500
        assert "X-Correlation-ID" in response.headers
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "DATABASE_ERROR"
        assert data["error"]["message"] == "Error interno del servidor - problema de base de datos"
        assert "correlation_id" in data["error"]
    
    def test_generic_error_handling(self):
        """Test manejo de errores genéricos"""
        response = client.get("/test/generic-error")
        
        assert response.status_code == 500
        assert "X-Correlation-ID" in response.headers
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
        assert data["error"]["message"] == "Error interno del servidor"
        assert "correlation_id" in data["error"]
    
    def test_correlation_id_consistency(self):
        """Test que correlation ID es consistente durante la request"""
        response = client.get("/test/correlation-id")
        
        assert response.status_code == 200
        
        # Correlation ID en header debe coincidir con el del body
        header_correlation_id = response.headers["X-Correlation-ID"]
        body_correlation_id = response.json()["correlation_id"]
        
        assert header_correlation_id == body_correlation_id
        assert header_correlation_id is not None
    
    def test_error_response_format_consistency(self):
        """Test que todas las respuestas de error tienen formato consistente"""
        # Test diferentes tipos de errores
        error_endpoints = [
            ("/test/http-exception", 404),
            ("/test/database-error", 500),
            ("/test/generic-error", 500)
        ]
        
        for endpoint, expected_status in error_endpoints:
            response = client.get(endpoint)
            
            assert response.status_code == expected_status
            assert "X-Correlation-ID" in response.headers
            
            data = response.json()
            
            # Verificar estructura consistente
            assert "error" in data
            error = data["error"]
            
            required_fields = ["code", "message", "correlation_id", "timestamp", "path", "method"]
            for field in required_fields:
                assert field in error, f"Missing field {field} in error response for {endpoint}"
            
            assert error["path"] == endpoint
            assert error["method"] == "GET"
    
    def test_validation_error_details_format(self):
        """Test formato específico de detalles de errores de validación"""
        # Enviar múltiples errores de validación
        response = client.post("/test/validation-error", json={"name": 123, "age": "invalid"})
        
        assert response.status_code == 422
        data = response.json()
        
        assert "details" in data["error"]
        details = data["error"]["details"]
        
        # Debe haber al menos un error
        assert len(details) > 0
        
        # Verificar formato de cada detalle
        for detail in details:
            assert "field" in detail
            assert "message" in detail
            assert "type" in detail
            assert isinstance(detail["field"], str)
            assert isinstance(detail["message"], str)
            assert isinstance(detail["type"], str)
    
    @patch('middleware.error_handler.logger')
    def test_error_logging(self, mock_logger):
        """Test que los errores se loggean correctamente"""
        # Trigger database error
        response = client.get("/test/database-error")
        
        assert response.status_code == 500
        
        # Verificar que se loggeó el error
        mock_logger.error.assert_called()
        
        # Verificar argumentos del log
        call_args = mock_logger.error.call_args
        assert "Database error - Correlation ID:" in call_args[0][0]
        assert "extra" in call_args[1]
        assert "correlation_id" in call_args[1]["extra"]
    
    def test_get_correlation_id_utility(self):
        """Test función utilitaria get_correlation_id"""
        # Mock request con correlation_id
        mock_request = MagicMock()
        mock_request.state.correlation_id = "test-correlation-id"
        
        correlation_id = get_correlation_id(mock_request)
        assert correlation_id == "test-correlation-id"
        
        # Mock request sin correlation_id
        mock_request_no_id = MagicMock()
        del mock_request_no_id.state.correlation_id
        
        correlation_id_none = get_correlation_id(mock_request_no_id)
        assert correlation_id_none is None
    
    @patch('middleware.error_handler.logging.getLogger')
    def test_log_with_correlation_utility(self, mock_get_logger):
        """Test función utilitaria log_with_correlation"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Mock request con correlation_id
        mock_request = MagicMock()
        mock_request.state.correlation_id = "test-correlation-id"
        
        log_with_correlation(
            mock_logger,
            "info",
            "Test message",
            mock_request,
            extra={"additional": "data"}
        )
        
        # Verificar que se llamó el método correcto del logger
        mock_logger.info.assert_called_once()
        
        # Verificar argumentos
        call_args = mock_logger.info.call_args
        assert "Test message - Correlation ID: test-correlation-id" in call_args[0][0]
        assert "extra" in call_args[1]
        assert call_args[1]["extra"]["correlation_id"] == "test-correlation-id"
        assert call_args[1]["extra"]["additional"] == "data"