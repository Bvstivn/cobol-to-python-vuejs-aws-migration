"""
Router de gestión de tarjetas de crédito para CardDemo API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from database import get_session
from dependencies import get_current_active_user
from services.card_service import CardService
from services.account_service import AccountService
from models.api_models import CardResponse
from models.database_models import User


router = APIRouter(prefix="/cards", tags=["cards"])


def get_card_service() -> CardService:
    """Dependency para obtener servicio de tarjetas"""
    return CardService()


def get_account_service() -> AccountService:
    """Dependency para obtener servicio de cuentas"""
    return AccountService()


@router.get("", response_model=List[CardResponse])
async def get_my_cards(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
    card_service: CardService = Depends(get_card_service),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Obtener todas las tarjetas del usuario actual
    
    Args:
        current_user: Usuario actual autenticado
        session: Sesión de base de datos
        card_service: Servicio de tarjetas
        account_service: Servicio de cuentas
        
    Returns:
        Lista de tarjetas del usuario con números enmascarados
    """
    # Obtener o crear cuenta del usuario
    account = account_service.get_or_create_account(session, current_user.id)
    
    # Obtener tarjetas de la cuenta
    cards = card_service.get_cards_by_account_id(session, account.id)
    
    # Si no hay tarjetas, crear algunas de ejemplo para la demo
    if not cards:
        cards = card_service.create_sample_cards(session, account.id)
    
    # Convertir a modelos de respuesta con números enmascarados
    return [card_service.card_to_response(card) for card in cards]


@router.get("/{card_id}", response_model=CardResponse)
async def get_card_details(
    card_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
    card_service: CardService = Depends(get_card_service),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Obtener detalles de una tarjeta específica
    
    Args:
        card_id: ID de la tarjeta
        current_user: Usuario actual autenticado
        session: Sesión de base de datos
        card_service: Servicio de tarjetas
        account_service: Servicio de cuentas
        
    Returns:
        Detalles de la tarjeta con número enmascarado
        
    Raises:
        HTTPException: Si la tarjeta no existe o no pertenece al usuario
    """
    # Obtener o crear cuenta del usuario
    account = account_service.get_or_create_account(session, current_user.id)
    
    # Buscar la tarjeta verificando que pertenezca al usuario
    card = card_service.get_card_by_id(session, card_id, account.id)
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarjeta no encontrada o no tienes permisos para acceder a ella"
        )
    
    # Convertir a modelo de respuesta con número enmascarado
    return card_service.card_to_response(card)