"""
Tests de propiedades para manejo de errores y validación
"""
import pytest
from hypothesis import given, strategies as st, settings
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
import json
from datetime import datetime

from middleware.error_handler import ErrorHandlerMiddleware, setup_exception_handlers


# Crear app de prueba
test_app = FastAPI()
test_app.add_middleware(ErrorHandlerMiddleware)
setup_exception_handlers(test_app)


# Modelo de prueba
class TestModel(BaseModel):
    name: str
    age: int


# Endpoints de prueba para propiedades
@test_app.get("/prop/http-error/{status_code}")
async def prop_http_error(status_code: int):
    raise HTTPException(status_code=status_code, detail=f"Error {status_code}")


@test_app.post("/prop/validation")
async def prop_validation(data: TestModel):
    return {"data": data}


@test_app.get("/prop/database-error")
async def prop_database_error():
    raise SQLAlchemyError("Database error")


@test_app.get("/prop/generic-error")
async def prop_generic_error():
    raise ValueError("Generic error")


client = TestClient(test_app)


class TestErrorProperties:
    """Tests de propiedades para manejo de errores"""
    
    @given(
        status_code=st.integers(min_value=400, max_value=599)
    )
    @settings(max_examples=10)
    def test_property_json_format_consistency(self, status_code):
        """
        **Propiedad 20: Formato JSON consistente**
        **Valida: Requisitos 7.1**
        
        Todas las respuestas de error deben tener formato JSON consistente
        independientemente del tipo de error o código de estado.
        """
        # Generar error HTTP con código de estado aleatorio
        response = client.get(f"/prop/http-error/{status_code}")
        
        # Verificar que la respuesta es JSON válido
        assert response.headers.get("content-type") == "application/json"
        
        # Verificar que se puede parsear como JSON
        try:
            data = response.json()
        except json.JSONDecodeError:
            pytest.fail("La respuesta no es JSON válido")
        
        # Verificar estructura consistente de error
        assert isinstance(data, dict), "La respuesta debe ser un objeto JSON"
        assert "error" in data, "La respuesta debe contener campo 'error'"
        
        error = data["error"]
        assert isinstance(error, dict), "El campo 'error' debe ser un objeto"
        
        # Verificar campos requeridos en todas las respuestas de error
        required_fields = ["code", "message", "correlation_id", "timestamp", "path", "method"]
        for field in required_fields:
            assert field in error, f"Campo requerido '{field}' faltante en respuesta de error"
            assert error[field] is not None, f"Campo '{field}' no puede ser null"
            assert isinstance(error[field], str), f"Campo '{field}' debe ser string"
        
        # Verificar formato de timestamp
        try:
            datetime.fromisoformat(error["timestamp"].replace("Z", "+00:00"))
        except ValueError:
            pytest.fail("El timestamp debe estar en formato ISO 8601")
        
        # Verificar que correlation_id es un UUID válido
        correlation_id = error["correlation_id"]
        assert len(correlation_id) == 36, "Correlation ID debe tener formato UUID"
        assert correlation_id.count("-") == 4, "Correlation ID debe tener formato UUID"
    
    @given(
        invalid_data=st.one_of(
            st.dictionaries(st.text(), st.integers()),  # Datos con tipos incorrectos
            st.dictionaries(st.text(), st.none()),      # Datos con valores null
            st.just({}),                                # Objeto vacío
            st.just({"name": "test"}),                  # Campos faltantes
            st.just({"age": 25})                        # Campos faltantes
        )
    )
    @settings(max_examples=10)
    def test_property_validation_error_format(self, invalid_data):
        """
        **Propiedad 21: Validación de esquemas de entrada**
        **Valida: Requisitos 7.2**
        
        Los errores de validación deben tener formato consistente
        con detalles específicos sobre los campos inválidos.
        """
        response = client.post("/prop/validation", json=invalid_data)
        
        # Debe ser error de validación
        assert response.status_code == 422
        
        data = response.json()
        assert "error" in data
        
        error = data["error"]
        assert error["code"] == "VALIDATION_ERROR"
        assert "details" in error
        assert isinstance(error["details"], list)
        
        # Si hay detalles, verificar formato
        if error["details"]:
            for detail in error["details"]:
                assert isinstance(detail, dict)
                assert "field" in detail
                assert "message" in detail
                assert "type" in detail
                assert isinstance(detail["field"], str)
                assert isinstance(detail["message"], str)
                assert isinstance(detail["type"], str)
    
    @given(
        error_type=st.sampled_from(["http", "validation", "database", "generic"])
    )
    @settings(max_examples=10)
    def test_property_error_handling_consistency(self, error_type):
        """
        **Propiedad 22: Manejo consistente de errores de validación**
        **Valida: Requisitos 2.3, 7.3**
        
        Todos los tipos de errores deben manejarse de manera consistente
        con el mismo formato de respuesta y headers.
        """
        # Generar diferentes tipos de errores
        if error_type == "http":
            response = client.get("/prop/http-error/404")
        elif error_type == "validation":
            response = client.post("/prop/validation", json={"invalid": "data"})
        elif error_type == "database":
            response = client.get("/prop/database-error")
        else:  # generic
            response = client.get("/prop/generic-error")
        
        # Verificar que todas las respuestas de error tienen correlation ID
        assert "X-Correlation-ID" in response.headers
        correlation_id_header = response.headers["X-Correlation-ID"]
        
        # Verificar formato de respuesta consistente
        data = response.json()
        assert "error" in data
        
        error = data["error"]
        assert "correlation_id" in error
        
        # Correlation ID en header debe coincidir con el del body
        assert correlation_id_header == error["correlation_id"]
        
        # Verificar campos comunes en todos los tipos de error
        common_fields = ["code", "message", "timestamp", "path", "method"]
        for field in common_fields:
            assert field in error
            assert isinstance(error[field], str)
    
    @given(
        status_codes=st.lists(
            st.integers(min_value=400, max_value=599),
            min_size=2,
            max_size=5,
            unique=True
        )
    )
    @settings(max_examples=10)
    def test_property_http_status_codes(self, status_codes):
        """
        **Propiedad 23: Códigos de estado HTTP apropiados**
        **Valida: Requisitos 7.4**
        
        Los códigos de estado HTTP en las respuestas deben coincidir
        con los códigos especificados en las excepciones.
        """
        for status_code in status_codes:
            response = client.get(f"/prop/http-error/{status_code}")
            
            # El código de estado de la respuesta debe coincidir
            assert response.status_code == status_code
            
            # Verificar que el error contiene información sobre el código
            data = response.json()
            error = data["error"]
            
            # El mensaje debe reflejar el código de estado
            assert str(status_code) in error["message"]
    
    @given(
        requests_count=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=10)
    def test_property_correlation_ids_unique(self, requests_count):
        """
        **Propiedad 24: IDs de correlación en respuestas**
        **Valida: Requisitos 7.5**
        
        Cada request debe tener un correlation ID único,
        incluso cuando se hacen múltiples requests similares.
        """
        correlation_ids = set()
        
        for _ in range(requests_count):
            response = client.get("/prop/http-error/404")
            
            # Verificar que tiene correlation ID
            assert "X-Correlation-ID" in response.headers
            correlation_id = response.headers["X-Correlation-ID"]
            
            # Verificar que es único
            assert correlation_id not in correlation_ids, "Correlation IDs deben ser únicos"
            correlation_ids.add(correlation_id)
            
            # Verificar formato UUID
            assert len(correlation_id) == 36
            assert correlation_id.count("-") == 4
            
            # Verificar que también está en el body
            data = response.json()
            assert data["error"]["correlation_id"] == correlation_id