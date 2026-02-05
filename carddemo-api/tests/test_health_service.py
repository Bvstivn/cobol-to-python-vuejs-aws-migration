"""
Tests para el servicio de salud del sistema
"""
import pytest
import time
from unittest.mock import patch, MagicMock
from sqlmodel import Session

from services.health_service import HealthService, health_service


class TestHealthService:
    """Tests para HealthService"""
    
    def test_get_basic_health(self):
        """Test para obtener información básica de salud"""
        service = HealthService()
        health_data = service.get_basic_health()
        
        assert health_data["status"] == "healthy"
        assert health_data["service"] == "CardDemo API"
        assert health_data["version"] == "1.0.0"
        assert "timestamp" in health_data
    
    def test_get_detailed_health_with_healthy_database(self):
        """Test para obtener información detallada con base de datos saludable"""
        service = HealthService()
        
        # Mock de la verificación de base de datos
        with patch.object(service, '_check_database_health') as mock_db_check:
            mock_db_check.return_value = {
                "status": "connected",
                "response_time_ms": 5.2
            }
            
            health_data = service.get_detailed_health()
            
            assert health_data["status"] == "healthy"
            assert health_data["database"]["status"] == "connected"
            assert health_data["database"]["response_time_ms"] == 5.2
            assert "uptime" in health_data
            assert health_data["uptime"] >= 0
    
    def test_get_detailed_health_with_unhealthy_database(self):
        """Test para obtener información detallada con base de datos no saludable"""
        service = HealthService()
        
        # Mock de la verificación de base de datos con error
        with patch.object(service, '_check_database_health') as mock_db_check:
            mock_db_check.return_value = {
                "status": "error",
                "error": "Connection failed"
            }
            
            health_data = service.get_detailed_health()
            
            assert health_data["status"] == "degraded"
            assert health_data["database"]["status"] == "error"
            assert health_data["database"]["error"] == "Connection failed"
    
    @patch('services.health_service.get_session')
    def test_check_database_health_success(self, mock_get_session):
        """Test para verificación exitosa de base de datos"""
        service = HealthService()
        
        # Mock de la sesión y query
        mock_session = MagicMock()
        mock_session.exec.return_value.first.return_value = 1
        mock_get_session.return_value = iter([mock_session])
        
        result = service._check_database_health()
        
        assert result["status"] == "connected"
        assert "response_time_ms" in result
        assert result["response_time_ms"] >= 0
        mock_session.close.assert_called_once()
    
    @patch('services.health_service.get_session')
    def test_check_database_health_failure(self, mock_get_session):
        """Test para fallo en verificación de base de datos"""
        service = HealthService()
        
        # Mock de excepción en la sesión
        mock_get_session.side_effect = Exception("Database connection failed")
        
        result = service._check_database_health()
        
        assert result["status"] == "error"
        assert result["error"] == "Database connection failed"
        assert result["response_time_ms"] is None
    
    def test_check_component_health_database(self):
        """Test para verificación de salud del componente database"""
        service = HealthService()
        
        with patch.object(service, '_check_database_health') as mock_db_check:
            mock_db_check.return_value = {"status": "connected"}
            
            result = service.check_component_health("database")
            
            assert result["status"] == "connected"
            mock_db_check.assert_called_once()
    
    def test_check_component_health_api(self):
        """Test para verificación de salud del componente api"""
        service = HealthService()
        
        result = service.check_component_health("api")
        
        assert result["status"] == "healthy"
        assert "uptime" in result
    
    def test_check_component_health_unknown(self):
        """Test para verificación de componente desconocido"""
        service = HealthService()
        
        result = service.check_component_health("unknown_component")
        
        assert result["status"] == "unknown"
        assert "Unknown component" in result["error"]
    
    def test_uptime_calculation(self):
        """Test para verificar cálculo de uptime"""
        service = HealthService()
        
        # Esperar un poco para que el uptime sea > 0
        time.sleep(0.01)
        
        with patch.object(service, '_check_database_health') as mock_db_check:
            mock_db_check.return_value = {"status": "connected"}
            
            health_data = service.get_detailed_health()
            
            assert health_data["uptime"] > 0
    
    def test_global_health_service_instance(self):
        """Test para verificar que la instancia global existe"""
        assert health_service is not None
        assert isinstance(health_service, HealthService)
        
        # Verificar que funciona
        basic_health = health_service.get_basic_health()
        assert basic_health["status"] == "healthy"