"""
Servicio de monitoreo de salud del sistema para CardDemo API
"""
import time
from typing import Dict, Any
from datetime import datetime, timezone

from database import check_database_health
from config import settings
from services.logging_service import get_secure_logger

logger = get_secure_logger("health")


class HealthService:
    """Servicio para monitoreo de salud del sistema"""
    
    def __init__(self):
        self.start_time = time.time()
    
    def get_basic_health(self) -> Dict[str, Any]:
        """
        Obtener estado básico de salud del sistema
        
        Returns:
            Diccionario con información básica de salud
        """
        logger.debug("Verificando salud básica del sistema")
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
            "timestamp": datetime.now(timezone.utc)
        }
    
    def get_detailed_health(self) -> Dict[str, Any]:
        """
        Obtener estado detallado de salud del sistema con métricas
        
        Returns:
            Diccionario con información detallada de salud y métricas
        """
        logger.debug("Verificando salud detallada del sistema")
        
        # Información básica
        health_info = self.get_basic_health()
        
        # Verificar conectividad de base de datos usando la nueva función
        database_status = check_database_health()
        
        # Calcular uptime
        uptime = time.time() - self.start_time
        
        # Agregar información detallada
        health_info.update({
            "database": database_status,
            "uptime": uptime
        })
        
        # Determinar estado general basado en componentes
        if database_status["status"] != "healthy":
            health_info["status"] = "degraded"
            logger.warning("Sistema en estado degradado debido a problemas de base de datos")
        else:
            logger.debug("Sistema en estado saludable")
        
        return health_info
    
    def _check_database_health(self) -> Dict[str, Any]:
        """
        Verificar conectividad y rendimiento de la base de datos
        Delegado a la función mejorada en database.py
        
        Returns:
            Diccionario con estado de la base de datos
        """
        return check_database_health()
    
    def check_component_health(self, component: str) -> Dict[str, Any]:
        """
        Verificar salud de un componente específico del sistema
        
        Args:
            component: Nombre del componente a verificar
            
        Returns:
            Diccionario con estado del componente
        """
        logger.debug(f"Verificando salud del componente: {component}")
        
        if component == "database":
            return self._check_database_health()
        elif component == "api":
            return {
                "status": "healthy",
                "uptime": time.time() - self.start_time
            }
        elif component == "logging":
            # Verificar que el sistema de logging funciona
            try:
                logger.info("Test de logging para verificación de salud")
                return {
                    "status": "healthy",
                    "message": "Logging system operational"
                }
            except Exception as e:
                return {
                    "status": "error",
                    "error": f"Logging system error: {str(e)}"
                }
        else:
            logger.warning(f"Componente desconocido solicitado: {component}")
            return {
                "status": "unknown",
                "error": f"Unknown component: {component}"
            }


# Instancia global del servicio de salud
health_service = HealthService()