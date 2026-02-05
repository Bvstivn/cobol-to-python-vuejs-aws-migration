"""
Router de monitoreo de salud para CardDemo API
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from services.health_service import health_service
from models.api_models import HealthResponse, DetailedHealthResponse


router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def get_basic_health():
    """
    Endpoint básico de verificación de salud
    
    Este endpoint no requiere autenticación y proporciona información
    básica sobre el estado del servicio.
    
    Returns:
        Información básica de salud del sistema
    """
    try:
        health_data = health_service.get_basic_health()
        return HealthResponse(**health_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/detailed", response_model=DetailedHealthResponse)
async def get_detailed_health():
    """
    Endpoint detallado de verificación de salud
    
    Este endpoint no requiere autenticación y proporciona información
    detallada sobre el estado del sistema incluyendo métricas de
    base de datos y tiempo de actividad.
    
    Returns:
        Información detallada de salud del sistema con métricas
    """
    try:
        health_data = health_service.get_detailed_health()
        return DetailedHealthResponse(**health_data)
    except Exception as e:
        # Para el endpoint detallado, intentamos retornar información parcial
        # incluso si algunos componentes fallan
        try:
            basic_health = health_service.get_basic_health()
            # Agregar información de error para el componente que falló
            health_data = {
                **basic_health,
                "status": "degraded",
                "database": {
                    "status": "error",
                    "error": str(e),
                    "response_time_ms": None
                },
                "uptime": 0.0  # Fallback value
            }
            return DetailedHealthResponse(**health_data)
        except Exception:
            # Si todo falla, retornar 503
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Detailed health check failed: {str(e)}"
            )


@router.get("/component/{component_name}")
async def get_component_health(component_name: str) -> Dict[str, Any]:
    """
    Verificar salud de un componente específico del sistema
    
    Args:
        component_name: Nombre del componente (database, api)
        
    Returns:
        Estado del componente específico
    """
    try:
        component_health = health_service.check_component_health(component_name)
        
        # Si el componente es desconocido, retornar 500
        if component_health.get("status") == "unknown":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to check component {component_name}: {component_health.get('error', 'Unknown component')}"
            )
        
        # Si el componente tiene error, retornar 503
        if component_health.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Component {component_name} is unhealthy: {component_health.get('error', 'Unknown error')}"
            )
        
        return {
            "component": component_name,
            "health": component_health
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check component {component_name}: {str(e)}"
        )