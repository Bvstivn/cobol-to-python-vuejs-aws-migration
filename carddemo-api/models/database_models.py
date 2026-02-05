"""
Modelos de base de datos para CardDemo API usando SQLModel
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class User(SQLModel, table=True):
    """Modelo de usuario del sistema"""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=50)
    email: str = Field(unique=True, index=True, max_length=100)
    hashed_password: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relaciones
    account: Optional["Account"] = Relationship(back_populates="user")


class Account(SQLModel, table=True):
    """Modelo de cuenta de cliente"""
    __tablename__ = "accounts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    account_number: str = Field(unique=True, index=True, max_length=20)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=200)
    city: Optional[str] = Field(default=None, max_length=50)
    state: Optional[str] = Field(default=None, max_length=2)
    zip_code: Optional[str] = Field(default=None, max_length=10)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relaciones
    user: Optional[User] = Relationship(back_populates="account")
    credit_cards: List["CreditCard"] = Relationship(back_populates="account")


class CreditCard(SQLModel, table=True):
    """Modelo de tarjeta de crédito"""
    __tablename__ = "credit_cards"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="accounts.id", index=True)
    card_number: str = Field(index=True, max_length=20)  # Será encriptado
    card_type: str = Field(max_length=20)  # VISA, MASTERCARD, AMEX, etc.
    expiry_month: int = Field(ge=1, le=12)
    expiry_year: int = Field(ge=2024, le=2050)
    status: str = Field(default="ACTIVE", max_length=20)  # ACTIVE, BLOCKED, EXPIRED
    credit_limit: Decimal = Field(max_digits=10, decimal_places=2)
    available_credit: Decimal = Field(max_digits=10, decimal_places=2)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relaciones
    account: Optional[Account] = Relationship(back_populates="credit_cards")
    transactions: List["Transaction"] = Relationship(back_populates="credit_card")


class Transaction(SQLModel, table=True):
    """Modelo de transacción"""
    __tablename__ = "transactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    card_id: int = Field(foreign_key="credit_cards.id", index=True)
    transaction_date: datetime = Field(index=True)
    merchant_name: str = Field(max_length=100)
    amount: Decimal = Field(max_digits=10, decimal_places=2)
    transaction_type: str = Field(max_length=20)  # PURCHASE, PAYMENT, REFUND
    status: str = Field(default="COMPLETED", max_length=20)  # PENDING, COMPLETED, FAILED
    description: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relaciones
    credit_card: Optional[CreditCard] = Relationship(back_populates="transactions")


class AuditLog(SQLModel, table=True):
    """Modelo para auditoría de cambios"""
    __tablename__ = "audit_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    table_name: str = Field(max_length=50)
    record_id: int
    action: str = Field(max_length=20)  # CREATE, UPDATE, DELETE
    old_values: Optional[str] = Field(default=None)  # JSON string
    new_values: Optional[str] = Field(default=None)  # JSON string
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)