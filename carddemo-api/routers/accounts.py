"""
Router de gestión de cuentas para CardDemo API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from database import get_session
from dependencies import get_current_active_user
from services.account_service import AccountService
from models.api_models import AccountResponse, AccountUpdate
from models.database_models import User


router = APIRouter(prefix="/accounts", tags=["accounts"])


def get_account_service() -> AccountService:
    """Dependency para obtener servicio de cuentas"""
    return AccountService()


@router.get("/me", response_model=AccountResponse)
async def get_my_account(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Obtener información de la cuenta del usuario actual
    
    Args:
        current_user: Usuario actual autenticado
        session: Sesión de base de datos
        account_service: Servicio de cuentas
        
    Returns:
        Información de la cuenta del usuario
    """
    # Obtener o crear cuenta si no existe
    account = account_service.get_or_create_account(session, current_user.id)
    
    return AccountResponse(
        id=account.id,
        account_number=account.account_number,
        first_name=account.first_name,
        last_name=account.last_name,
        phone=account.phone,
        address=account.address,
        city=account.city,
        state=account.state,
        zip_code=account.zip_code,
        created_at=account.created_at,
        updated_at=account.updated_at
    )


@router.put("/me", response_model=AccountResponse)
async def update_my_account(
    account_update: AccountUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Actualizar información de la cuenta del usuario actual
    
    Args:
        account_update: Datos de actualización de la cuenta
        current_user: Usuario actual autenticado
        session: Sesión de base de datos
        account_service: Servicio de cuentas
        
    Returns:
        Información actualizada de la cuenta
        
    Raises:
        HTTPException: Si hay errores de validación
    """
    # Obtener o crear cuenta si no existe
    account = account_service.get_or_create_account(session, current_user.id)
    
    try:
        # Actualizar cuenta
        updated_account = account_service.update_account(session, account, account_update)
        
        return AccountResponse(
            id=updated_account.id,
            account_number=updated_account.account_number,
            first_name=updated_account.first_name,
            last_name=updated_account.last_name,
            phone=updated_account.phone,
            address=updated_account.address,
            city=updated_account.city,
            state=updated_account.state,
            zip_code=updated_account.zip_code,
            created_at=updated_account.created_at,
            updated_at=updated_account.updated_at
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar cuenta: {str(e)}"
        )