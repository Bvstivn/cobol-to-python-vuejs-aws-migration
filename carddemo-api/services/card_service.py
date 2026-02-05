"""
Servicio de gestión de tarjetas de crédito para CardDemo API
"""
from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime, timezone
from decimal import Decimal
import logging

from models.database_models import CreditCard, Account
from models.api_models import CardResponse
from services.encryption_service import get_encryption_service

logger = logging.getLogger(__name__)


class CardService:
    """Servicio para manejo de tarjetas de crédito con encriptación"""
    
    def __init__(self):
        self.encryption_service = get_encryption_service()
    
    def get_cards_by_account_id(self, session: Session, account_id: int) -> List[CreditCard]:
        """
        Obtener todas las tarjetas de una cuenta
        
        Args:
            session: Sesión de base de datos
            account_id: ID de la cuenta
            
        Returns:
            Lista de tarjetas de la cuenta
        """
        statement = select(CreditCard).where(CreditCard.account_id == account_id)
        return list(session.exec(statement).all())
    
    def get_card_by_id(self, session: Session, card_id: int, account_id: int) -> Optional[CreditCard]:
        """
        Obtener tarjeta específica por ID, verificando que pertenezca a la cuenta
        
        Args:
            session: Sesión de base de datos
            card_id: ID de la tarjeta
            account_id: ID de la cuenta (para verificar permisos)
            
        Returns:
            Tarjeta si existe y pertenece a la cuenta, None en caso contrario
        """
        statement = select(CreditCard).where(
            CreditCard.id == card_id,
            CreditCard.account_id == account_id
        )
        return session.exec(statement).first()
    
    def mask_card_number(self, card_number: str) -> str:
        """
        Enmascarar número de tarjeta usando el servicio de encriptación
        
        Args:
            card_number: Número de tarjeta (puede estar encriptado)
            
        Returns:
            Número enmascarado en formato "**** **** **** 1234"
        """
        try:
            return self.encryption_service.mask_card_number(card_number)
        except Exception as e:
            logger.error(f"Error masking card number: {e}")
            return "**** **** **** ****"
    
    def card_to_response(self, card: CreditCard) -> CardResponse:
        """
        Convertir modelo de base de datos a modelo de respuesta
        
        Args:
            card: Tarjeta de la base de datos
            
        Returns:
            Modelo de respuesta con número enmascarado
        """
        return CardResponse(
            id=card.id,
            masked_card_number=self.mask_card_number(card.card_number),
            card_type=card.card_type,
            expiry_month=card.expiry_month,
            expiry_year=card.expiry_year,
            status=card.status,
            credit_limit=card.credit_limit,
            available_credit=card.available_credit,
            created_at=card.created_at
        )
    
    def create_sample_cards(self, session: Session, account_id: int) -> List[CreditCard]:
        """
        Crear tarjetas de ejemplo para demostración con encriptación
        
        Args:
            session: Sesión de base de datos
            account_id: ID de la cuenta
            
        Returns:
            Lista de tarjetas creadas
        """
        sample_cards = [
            {
                "card_number": "4532123456781234",  # VISA
                "card_type": "VISA",
                "expiry_month": 12,
                "expiry_year": 2025,
                "credit_limit": Decimal("5000.00"),
                "available_credit": Decimal("4200.00")
            },
            {
                "card_number": "5555123456784321",  # MASTERCARD
                "card_type": "MASTERCARD", 
                "expiry_month": 8,
                "expiry_year": 2026,
                "credit_limit": Decimal("3000.00"),
                "available_credit": Decimal("2850.00")
            }
        ]
        
        created_cards = []
        for card_data in sample_cards:
            try:
                # Encriptar número de tarjeta antes de guardar
                encrypted_number = self.encryption_service.encrypt_card_number(card_data["card_number"])
                
                card = CreditCard(
                    account_id=account_id,
                    card_number=encrypted_number,  # Guardar encriptado
                    card_type=card_data["card_type"],
                    expiry_month=card_data["expiry_month"],
                    expiry_year=card_data["expiry_year"],
                    status="ACTIVE",
                    credit_limit=card_data["credit_limit"],
                    available_credit=card_data["available_credit"],
                    created_at=datetime.now(timezone.utc)
                )
                session.add(card)
                created_cards.append(card)
                
            except Exception as e:
                logger.error(f"Error creating sample card: {e}")
                continue
        
        if created_cards:
            session.commit()
            for card in created_cards:
                session.refresh(card)
        
        return created_cards
    
    def encrypt_existing_card_numbers(self, session: Session) -> int:
        """
        Encriptar números de tarjeta existentes que no estén encriptados
        (Función de migración)
        
        Args:
            session: Sesión de base de datos
            
        Returns:
            Número de tarjetas actualizadas
        """
        cards = session.exec(select(CreditCard)).all()
        updated_count = 0
        
        for card in cards:
            try:
                # Verificar si ya está encriptado (los números encriptados son más largos)
                if len(card.card_number) <= 20:  # Número sin encriptar
                    encrypted_number = self.encryption_service.encrypt_card_number(card.card_number)
                    card.card_number = encrypted_number
                    updated_count += 1
                    
            except Exception as e:
                logger.error(f"Error encrypting card {card.id}: {e}")
                continue
        
        if updated_count > 0:
            session.commit()
            logger.info(f"Encrypted {updated_count} card numbers")
        
        return updated_count