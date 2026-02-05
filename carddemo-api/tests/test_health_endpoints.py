"""
Tests para los endpoints de salud del sistema
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app
from services.health_service import health_service


client = TestClient(app)


class TestHealthEndpoints:
    """Tests para endpoints de salud"""
    
    def test_get_basic_health_success(self):
        """Test para endpoint básico de salud exitoso"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["service"] == "CardDemo API"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
    
    def test_get_basic_health_no_authentication_required(self):
        """Test para verificar que el endpoint básico no requiere autenticación"""
        # No incluir headers de autenticación
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    @patch.object(health_service, 'get_basic_health')
    def test_get_basic_health_service_failure(self, mock_get_basic_health):
        """Test para fallo en el servicio de salud básico"""
        mock_get_basic_health.side_effect = Exception("Service error")
        
        response = client.get("/health")
        
        assert response.status_code == 503
        assert "Health check failed" in response.json()["detail"]
    
    def test_get_detailed_health_success(self):
        """Test para endpoint detallado de salud exitoso"""
        response = client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] in ["healthy", "degraded"]
        assert data["service"] == "CardDemo API"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
        assert "database" in data
        assert "uptime" in data
        
        # Verificar estructura de database
        db_info = data["database"]
        assert "status" in db_info
        assert db_info["status"] in ["connected", "error"]
    
    def test_get_detailed_health_no_authentication_required(self):
        """Test para verificar que el endpoint detallado no requiere autenticación"""
        response = client.get("/health/detailed")
        
        assert response.status_code == 200
        assert "database" in response.json()
    
    @patch.object(health_service, 'get_detailed_health')
    def test_get_detailed_health_service_failure(self, mock_get_detailed_health):
        """Test para fallo en el servicio de salud detallado"""
        mock_get_detailed_health.side_effect = Exception("Detailed service error")
        
        response = client.get("/health/detailed")
        
        # El endpoint detallado ahora intenta retornar información parcial
        # incluso si algunos componentes fallan
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["database"]["status"] == "error"
        assert "Detailed service error" in data["database"]["error"]
    
    def test_get_component_health_database_success(self):
        """Test para verificación exitosa del componente database"""
        response = client.get("/health/component/database")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["component"] == "database"
        assert "health" in data
        assert data["health"]["status"] in ["connected", "error"]
    
    def test_get_component_health_api_success(self):
        """Test para verificación exitosa del componente api"""
        response = client.get("/health/component/api")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["component"] == "api"
        assert data["health"]["status"] == "healthy"
        assert "uptime" in data["health"]
    
    def test_get_component_health_unknown_component(self):
        """Test para componente desconocido"""
        response = client.get("/health/component/unknown")
        
        assert response.status_code == 500
        assert "Failed to check component unknown" in response.json()["detail"]
    
    @patch.object(health_service, 'check_component_health')
    def test_get_component_health_component_error(self, mock_check_component):
        """Test para componente con error"""
        mock_check_component.return_value = {
            "status": "error",
            "error": "Component is down"
        }
        
        response = client.get("/health/component/database")
        
        assert response.status_code == 503
        assert "Component database is unhealthy" in response.json()["detail"]
        assert "Component is down" in response.json()["detail"]
    
    @patch.object(health_service, 'check_component_health')
    def test_get_component_health_service_exception(self, mock_check_component):
        """Test para excepción en verificación de componente"""
        mock_check_component.side_effect = Exception("Service exception")
        
        response = client.get("/health/component/database")
        
        assert response.status_code == 500
        assert "Failed to check component database" in response.json()["detail"]
    
    def test_health_endpoints_response_format(self):
        """Test para verificar formato de respuesta de endpoints de salud"""
        # Test endpoint básico
        basic_response = client.get("/health")
        basic_data = basic_response.json()
        
        required_basic_fields = ["status", "service", "version", "timestamp"]
        for field in required_basic_fields:
            assert field in basic_data
        
        # Test endpoint detallado
        detailed_response = client.get("/health/detailed")
        detailed_data = detailed_response.json()
        
        required_detailed_fields = ["status", "service", "version", "timestamp", "database", "uptime"]
        for field in required_detailed_fields:
            assert field in detailed_data
        
        # Verificar que database tiene los campos requeridos
        db_data = detailed_data["database"]
        assert "status" in db_data
        
        if db_data["status"] == "connected":
            assert "response_time_ms" in db_data
        elif db_data["status"] == "error":
            assert "error" in db_data
    
    def test_health_endpoints_performance(self):
        """Test para verificar que los endpoints de salud responden rápidamente"""
        import time
        
        # Test endpoint básico
        start_time = time.time()
        response = client.get("/health")
        basic_time = time.time() - start_time
        
        assert response.status_code == 200
        assert basic_time < 1.0  # Debe responder en menos de 1 segundo
        
        # Test endpoint detallado
        start_time = time.time()
        response = client.get("/health/detailed")
        detailed_time = time.time() - start_time
        
        assert response.status_code == 200
        assert detailed_time < 2.0  # Debe responder en menos de 2 segundos