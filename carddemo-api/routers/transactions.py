"""
Router de gestión de transacciones para CardDemo API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import Optional
from datetime import date
from decimal import Decimal

from database import get_session
from dependencies import get_current_active_user
from services.transaction_service import TransactionService
from services.card_service import CardService
from models.api_models import TransactionResponse, TransactionListResponse, TransactionFilters, TransactionType
from models.database_models import User


router = APIRouter(prefix="/transactions", tags=["transactions"])


def get_transaction_service() -> TransactionService:
    """Dependency para obtener servicio de transacciones"""
    return TransactionService()


def get_card_service() -> CardService:
    """Dependency para obtener servicio de tarjetas"""
    return CardService()


@router.get("", response_model=TransactionListResponse)
async def get_my_transactions(
    start_date: Optional[date] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    card_id: Optional[int] = Query(None, ge=1, description="ID de la tarjeta"),
    transaction_type: Optional[TransactionType] = Query(None, description="Tipo de transacción"),
    min_amount: Optional[Decimal] = Query(None, ge=0, description="Monto mínimo"),
    max_amount: Optional[Decimal] = Query(None, ge=0, description="Monto máximo"),
    limit: int = Query(50, ge=1, le=100, description="Número máximo de resultados"),
    offset: int = Query(0, ge=0, description="Número de resultados a saltar"),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
    transaction_service: TransactionService = Depends(get_transaction_service),
    card_service: CardService = Depends(get_card_service)
):
    """
    Obtener transacciones del usuario actual con filtros opcionales
    
    Args:
        start_date: Fecha de inicio para filtrar transacciones
        end_date: Fecha de fin para filtrar transacciones
        card_id: ID de tarjeta específica para filtrar
        transaction_type: Tipo de transacción para filtrar
        min_amount: Monto mínimo para filtrar
        max_amount: Monto máximo para filtrar
        limit: Número máximo de resultados por página
        offset: Número de resultados a saltar (para paginación)
        current_user: Usuario actual autenticado
        session: Sesión de base de datos
        transaction_service: Servicio de transacciones
        card_service: Servicio de tarjetas
        
    Returns:
        Lista paginada de transacciones del usuario con filtros aplicados
    """
    # Crear objeto de filtros
    filters = TransactionFilters(
        start_date=start_date,
        end_date=end_date,
        card_id=card_id,
        transaction_type=transaction_type,
        min_amount=min_amount,
        max_amount=max_amount,
        limit=limit,
        offset=offset
    )
    
    # Obtener transacciones con filtros
    transactions, total = transaction_service.get_transactions_with_filters(
        session, current_user.id, filters
    )
    
    # Si no hay transacciones, crear algunas de ejemplo
    if not transactions and offset == 0:  # Solo crear ejemplos en la primera página
        # Obtener tarjetas del usuario
        user_card_ids = transaction_service.get_user_card_ids(session, current_user.id)
        
        # Si no hay tarjetas, crear algunas primero
        if not user_card_ids:
            from services.account_service import AccountService
            account_service = AccountService()
            account = account_service.get_or_create_account(session, current_user.id)
            cards = card_service.create_sample_cards(session, account.id)
            user_card_ids = [card.id for card in cards]
        
        # Crear transacciones de ejemplo
        sample_transactions = transaction_service.create_sample_transactions(session, user_card_ids)
        
        # Volver a obtener transacciones con filtros
        transactions, total = transaction_service.get_transactions_with_filters(
            session, current_user.id, filters
        )
    
    # Convertir a modelos de respuesta
    transaction_responses = [
        transaction_service.transaction_to_response(transaction)
        for transaction in transactions
    ]
    
    # Calcular si hay más resultados
    has_more = (offset + len(transactions)) < total
    
    return TransactionListResponse(
        transactions=transaction_responses,
        total=total,
        limit=limit,
        offset=offset,
        has_more=has_more
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction_details(
    transaction_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """
    Obtener detalles de una transacción específica
    
    Args:
        transaction_id: ID de la transacción
        current_user: Usuario actual autenticado
        session: Sesión de base de datos
        transaction_service: Servicio de transacciones
        
    Returns:
        Detalles de la transacción
        
    Raises:
        HTTPException: Si la transacción no existe o no pertenece al usuario
    """
    # Buscar la transacción verificando que pertenezca al usuario
    transaction = transaction_service.get_transaction_by_id(
        session, transaction_id, current_user.id
    )
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transacción no encontrada o no tienes permisos para acceder a ella"
        )
    
    # Convertir a modelo de respuesta
    return transaction_service.transaction_to_response(transaction)