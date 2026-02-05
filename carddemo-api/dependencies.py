"""
Dependencias de FastAPI para CardDemo API
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from typing import Optional

from database import get_session
from services.auth_service import AuthService
from models.database_models import User


# Configurar esquema de seguridad Bearer
security = HTTPBearer()


def get_auth_service() -> AuthService:
    """Dependency para obtener servicio de autenticación"""
    return AuthService()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """
    Dependency para obtener usuario actual desde token JWT
    
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    token = credentials.credentials
    user = auth_service.get_current_user(session, token)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency para obtener usuario actual activo
    
    Raises:
        HTTPException: Si el usuario está inactivo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: Session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """
    Dependency para obtener usuario actual opcional (para endpoints públicos)
    
    Returns:
        Usuario si el token es válido, None si no hay token o es inválido
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    return auth_service.get_current_user(session, token)