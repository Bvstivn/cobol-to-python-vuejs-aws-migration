"""
Servicio de gestión de cuentas para CardDemo API
"""
from typing import Optional
from sqlmodel import Session, select
from datetime import datetime, timezone

from models.database_models import Account, User
from models.api_models import AccountUpdate


class AccountService:
    """Servicio para manejo de cuentas de usuario"""
    
    def get_account_by_user_id(self, session: Session, user_id: int) -> Optional[Account]:
        """
        Obtener cuenta por ID de usuario
        
        Args:
            session: Sesión de base de datos
            user_id: ID del usuario
            
        Returns:
            Cuenta del usuario o None si no existe
        """
        statement = select(Account).where(Account.user_id == user_id)
        return session.exec(statement).first()
    
    def create_account(self, session: Session, user_id: int, account_data: dict) -> Account:
        """
        Crear nueva cuenta para un usuario
        
        Args:
            session: Sesión de base de datos
            user_id: ID del usuario
            account_data: Datos de la cuenta
            
        Returns:
            Cuenta creada
        """
        # Generar número de cuenta único (simplificado para demo)
        import random
        account_number = f"ACC{random.randint(100000, 999999):06d}"
        
        account = Account(
            user_id=user_id,
            account_number=account_number,
            first_name=account_data.get("first_name", ""),
            last_name=account_data.get("last_name", ""),
            phone=account_data.get("phone"),
            address=account_data.get("address"),
            city=account_data.get("city"),
            state=account_data.get("state"),
            zip_code=account_data.get("zip_code"),
            created_at=datetime.now(timezone.utc)
        )
        
        session.add(account)
        session.commit()
        session.refresh(account)
        return account
    
    def update_account(self, session: Session, account: Account, update_data: AccountUpdate) -> Account:
        """
        Actualizar información de cuenta
        
        Args:
            session: Sesión de base de datos
            account: Cuenta a actualizar
            update_data: Datos de actualización
            
        Returns:
            Cuenta actualizada
        """
        # Actualizar solo los campos proporcionados
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            if hasattr(account, field):
                setattr(account, field, value)
        
        account.updated_at = datetime.now(timezone.utc)
        
        session.add(account)
        session.commit()
        session.refresh(account)
        return account
    
    def get_or_create_account(self, session: Session, user_id: int) -> Account:
        """
        Obtener cuenta existente o crear una nueva si no existe
        
        Args:
            session: Sesión de base de datos
            user_id: ID del usuario
            
        Returns:
            Cuenta del usuario
        """
        account = self.get_account_by_user_id(session, user_id)
        
        if not account:
            # Crear cuenta básica si no existe
            account = self.create_account(session, user_id, {
                "first_name": "",
                "last_name": ""
            })
        
        return account