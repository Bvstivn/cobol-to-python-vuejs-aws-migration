"""
Servicio de gestión de transacciones para CardDemo API
"""
from typing import List, Optional, Tuple
from sqlmodel import Session, select, and_, or_
from datetime import datetime, timezone, date
from decimal import Decimal

from models.database_models import Transaction, CreditCard, Account
from models.api_models import TransactionResponse, TransactionFilters, TransactionListResponse


class TransactionService:
    """Servicio para manejo de transacciones"""
    
    def get_user_card_ids(self, session: Session, user_id: int) -> List[int]:
        """
        Obtener IDs de todas las tarjetas del usuario
        
        Args:
            session: Sesión de base de datos
            user_id: ID del usuario
            
        Returns:
            Lista de IDs de tarjetas del usuario
        """
        # Obtener cuenta del usuario
        account_statement = select(Account).where(Account.user_id == user_id)
        account = session.exec(account_statement).first()
        
        if not account:
            return []
        
        # Obtener IDs de tarjetas de la cuenta
        cards_statement = select(CreditCard.id).where(CreditCard.account_id == account.id)
        card_ids = list(session.exec(cards_statement).all())
        
        return card_ids
    
    def get_transactions_with_filters(
        self, 
        session: Session, 
        user_id: int, 
        filters: TransactionFilters
    ) -> Tuple[List[Transaction], int]:
        """
        Obtener transacciones del usuario con filtros aplicados
        
        Args:
            session: Sesión de base de datos
            user_id: ID del usuario
            filters: Filtros a aplicar
            
        Returns:
            Tupla con (lista de transacciones, total de transacciones)
        """
        # Obtener IDs de tarjetas del usuario
        user_card_ids = self.get_user_card_ids(session, user_id)
        
        if not user_card_ids:
            return [], 0
        
        # Construir query base
        base_query = select(Transaction).where(Transaction.card_id.in_(user_card_ids))
        count_query = select(Transaction.id).where(Transaction.card_id.in_(user_card_ids))
        
        # Aplicar filtros
        conditions = []
        
        # Filtro por fechas
        if filters.start_date:
            start_datetime = datetime.combine(filters.start_date, datetime.min.time())
            conditions.append(Transaction.transaction_date >= start_datetime)
        
        if filters.end_date:
            end_datetime = datetime.combine(filters.end_date, datetime.max.time())
            conditions.append(Transaction.transaction_date <= end_datetime)
        
        # Filtro por tarjeta específica
        if filters.card_id:
            # Verificar que la tarjeta pertenezca al usuario
            if filters.card_id in user_card_ids:
                conditions.append(Transaction.card_id == filters.card_id)
            else:
                # Si la tarjeta no pertenece al usuario, no retornar nada
                return [], 0
        
        # Filtro por tipo de transacción
        if filters.transaction_type:
            conditions.append(Transaction.transaction_type == filters.transaction_type.value)
        
        # Filtro por monto
        if filters.min_amount is not None:
            conditions.append(Transaction.amount >= filters.min_amount)
        
        if filters.max_amount is not None:
            conditions.append(Transaction.amount <= filters.max_amount)
        
        # Aplicar condiciones a las queries
        if conditions:
            base_query = base_query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Obtener total de registros
        total = len(list(session.exec(count_query).all()))
        
        # Aplicar ordenamiento, paginación y ejecutar
        transactions = list(session.exec(
            base_query
            .order_by(Transaction.transaction_date.desc())
            .offset(filters.offset)
            .limit(filters.limit)
        ).all())
        
        return transactions, total
    
    def get_transaction_by_id(self, session: Session, transaction_id: int, user_id: int) -> Optional[Transaction]:
        """
        Obtener transacción específica por ID, verificando que pertenezca al usuario
        
        Args:
            session: Sesión de base de datos
            transaction_id: ID de la transacción
            user_id: ID del usuario (para verificar permisos)
            
        Returns:
            Transacción si existe y pertenece al usuario, None en caso contrario
        """
        # Obtener IDs de tarjetas del usuario
        user_card_ids = self.get_user_card_ids(session, user_id)
        
        if not user_card_ids:
            return None
        
        # Buscar la transacción
        statement = select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.card_id.in_(user_card_ids)
        )
        
        return session.exec(statement).first()
    
    def transaction_to_response(self, transaction: Transaction) -> TransactionResponse:
        """
        Convertir modelo de base de datos a modelo de respuesta
        
        Args:
            transaction: Transacción de la base de datos
            
        Returns:
            Modelo de respuesta
        """
        return TransactionResponse(
            id=transaction.id,
            transaction_date=transaction.transaction_date,
            merchant_name=transaction.merchant_name,
            amount=transaction.amount,
            transaction_type=transaction.transaction_type,
            status=transaction.status,
            description=transaction.description,
            created_at=transaction.created_at
        )
    
    def create_sample_transactions(self, session: Session, card_ids: List[int]) -> List[Transaction]:
        """
        Crear transacciones de ejemplo para demostración
        
        Args:
            session: Sesión de base de datos
            card_ids: IDs de las tarjetas para las que crear transacciones
            
        Returns:
            Lista de transacciones creadas
        """
        if not card_ids:
            return []
        
        sample_transactions = [
            {
                "merchant_name": "Amazon",
                "amount": Decimal("89.99"),
                "transaction_type": "PURCHASE",
                "description": "Online purchase - Electronics",
                "days_ago": 1
            },
            {
                "merchant_name": "Starbucks",
                "amount": Decimal("4.75"),
                "transaction_type": "PURCHASE",
                "description": "Coffee and pastry",
                "days_ago": 2
            },
            {
                "merchant_name": "Shell Gas Station",
                "amount": Decimal("45.20"),
                "transaction_type": "PURCHASE",
                "description": "Fuel purchase",
                "days_ago": 3
            },
            {
                "merchant_name": "Payment Received",
                "amount": Decimal("200.00"),
                "transaction_type": "PAYMENT",
                "description": "Credit card payment",
                "days_ago": 5
            },
            {
                "merchant_name": "Walmart",
                "amount": Decimal("67.43"),
                "transaction_type": "PURCHASE",
                "description": "Groceries",
                "days_ago": 7
            }
        ]
        
        created_transactions = []
        
        for i, transaction_data in enumerate(sample_transactions):
            # Alternar entre tarjetas disponibles
            card_id = card_ids[i % len(card_ids)]
            
            # Calcular fecha de transacción
            from datetime import timedelta
            transaction_date = datetime.now(timezone.utc) - timedelta(days=transaction_data["days_ago"])
            
            # Crear transacción
            transaction = Transaction(
                card_id=card_id,
                transaction_date=transaction_date,
                merchant_name=transaction_data["merchant_name"],
                amount=transaction_data["amount"],
                transaction_type=transaction_data["transaction_type"],
                status="COMPLETED",
                description=transaction_data["description"],
                created_at=datetime.now(timezone.utc)
            )
            
            session.add(transaction)
            created_transactions.append(transaction)
        
        session.commit()
        for transaction in created_transactions:
            session.refresh(transaction)
        
        return created_transactions