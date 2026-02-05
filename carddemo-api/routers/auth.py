"""
Router de autenticación para CardDemo API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session

from database import get_session
from dependencies import get_auth_service, get_current_active_user, security
from services.auth_service import AuthService
from models.api_models import UserLogin, TokenResponse, UserResponse
from models.database_models import User


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    user_credentials: UserLogin,
    session: Session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Autenticar usuario y generar token JWT
    
    Args:
        user_credentials: Credenciales de usuario (username y password)
        session: Sesión de base de datos
        auth_service: Servicio de autenticación
        
    Returns:
        Token JWT y información del usuario
        
    Raises:
        HTTPException: Si las credenciales son inválidas
    """
    # Autenticar usuario
    user = auth_service.authenticate_user(
        session, 
        user_credentials.username, 
        user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token JWT
    token_data = auth_service.create_user_token_data(user)
    access_token = auth_service.create_access_token(token_data)
    
    # Crear respuesta con información del usuario
    user_info = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=auth_service.access_token_expire_minutes * 60,  # Convertir minutos a segundos
        user=user_info
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Cerrar sesión del usuario
    
    Nota: En JWT stateless, el logout es principalmente del lado del cliente.
    El servidor simplemente confirma que el token era válido.
    
    Args:
        current_user: Usuario actual autenticado
        
    Returns:
        Mensaje de confirmación de logout
    """
    return {
        "message": f"Usuario {current_user.username} ha cerrado sesión exitosamente",
        "detail": "Token JWT debe ser eliminado del cliente"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener información del usuario actual
    
    Args:
        current_user: Usuario actual autenticado
        
    Returns:
        Información del usuario actual
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active
    )