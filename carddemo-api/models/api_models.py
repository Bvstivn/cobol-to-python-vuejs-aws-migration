"""
Modelos Pydantic para requests y responses de la API CardDemo
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# Enums para valores constantes
class CardType(str, Enum):
    VISA = "VISA"
    MASTERCARD = "MASTERCARD"
    AMEX = "AMEX"
    DISCOVER = "DISCOVER"


class CardStatus(str, Enum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    EXPIRED = "EXPIRED"


class TransactionType(str, Enum):
    PURCHASE = "PURCHASE"
    PAYMENT = "PAYMENT"
    REFUND = "REFUND"


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# Modelos de Request (entrada)
class UserLogin(BaseModel):
    """Modelo para login de usuario"""
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")
    password: str = Field(..., min_length=8, max_length=128, description="Contraseña del usuario")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "USER0001",
                "password": "PASSWORD"
            }
        }


class AccountUpdate(BaseModel):
    """Modelo para actualización de cuenta"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Nombre")
    last_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Apellido")
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono")
    address: Optional[str] = Field(None, min_length=5, max_length=200, description="Dirección")
    city: Optional[str] = Field(None, min_length=2, max_length=50, description="Ciudad")
    state: Optional[str] = Field(None, min_length=2, max_length=2, description="Estado (código de 2 letras)")
    zip_code: Optional[str] = Field(None, min_length=5, max_length=10, description="Código postal")
    
    @validator('state')
    def validate_state(cls, v):
        if v is not None:
            return v.upper()
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            # Remover caracteres no numéricos para validación básica
            digits_only = ''.join(filter(str.isdigit, v))
            if len(digits_only) < 10:
                raise ValueError('El teléfono debe tener al menos 10 dígitos')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "phone": "555-0123",
                "address": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip_code": "12345"
            }
        }


class TransactionFilters(BaseModel):
    """Modelo para filtros de transacciones"""
    start_date: Optional[date] = Field(None, description="Fecha de inicio (YYYY-MM-DD)")
    end_date: Optional[date] = Field(None, description="Fecha de fin (YYYY-MM-DD)")
    card_id: Optional[int] = Field(None, ge=1, description="ID de la tarjeta")
    transaction_type: Optional[TransactionType] = Field(None, description="Tipo de transacción")
    min_amount: Optional[Decimal] = Field(None, ge=0, description="Monto mínimo")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="Monto máximo")
    limit: int = Field(50, ge=1, le=100, description="Número máximo de resultados")
    offset: int = Field(0, ge=0, description="Número de resultados a saltar")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if v is not None and 'start_date' in values and values['start_date'] is not None:
            if v < values['start_date']:
                raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v
    
    @validator('max_amount')
    def validate_amount_range(cls, v, values):
        if v is not None and 'min_amount' in values and values['min_amount'] is not None:
            if v < values['min_amount']:
                raise ValueError('El monto máximo debe ser mayor al monto mínimo')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "transaction_type": "PURCHASE",
                "min_amount": 10.00,
                "max_amount": 1000.00,
                "limit": 20,
                "offset": 0
            }
        }


# Modelos de Response (salida)
class UserResponse(BaseModel):
    """Modelo para respuesta de información de usuario"""
    id: int = Field(..., description="ID único del usuario")
    username: str = Field(..., description="Nombre de usuario")
    email: str = Field(..., description="Email del usuario")
    is_active: bool = Field(..., description="Estado activo del usuario")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "username": "USER0001",
                "email": "user@carddemo.com",
                "is_active": True
            }
        }


class TokenResponse(BaseModel):
    """Modelo para respuesta de token de autenticación"""
    access_token: str = Field(..., description="Token JWT de acceso")
    token_type: str = Field("bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")
    user: UserResponse = Field(..., description="Información del usuario autenticado")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": 1,
                    "username": "USER0001",
                    "email": "user@carddemo.com",
                    "is_active": True
                }
            }
        }


class AccountResponse(BaseModel):
    """Modelo para respuesta de información de cuenta"""
    id: int = Field(..., description="ID único de la cuenta")
    account_number: str = Field(..., description="Número de cuenta")
    first_name: str = Field(..., description="Nombre")
    last_name: str = Field(..., description="Apellido")
    phone: Optional[str] = Field(None, description="Teléfono")
    address: Optional[str] = Field(None, description="Dirección")
    city: Optional[str] = Field(None, description="Ciudad")
    state: Optional[str] = Field(None, description="Estado")
    zip_code: Optional[str] = Field(None, description="Código postal")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "account_number": "1000000001",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "555-0123",
                "address": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip_code": "12345",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": None
            }
        }


class CardResponse(BaseModel):
    """Modelo para respuesta de información de tarjeta de crédito"""
    id: int = Field(..., description="ID único de la tarjeta")
    masked_card_number: str = Field(..., description="Número de tarjeta enmascarado")
    card_type: CardType = Field(..., description="Tipo de tarjeta")
    expiry_month: int = Field(..., ge=1, le=12, description="Mes de expiración")
    expiry_year: int = Field(..., ge=2024, description="Año de expiración")
    status: CardStatus = Field(..., description="Estado de la tarjeta")
    credit_limit: Decimal = Field(..., description="Límite de crédito")
    available_credit: Decimal = Field(..., description="Crédito disponible")
    created_at: datetime = Field(..., description="Fecha de creación")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "masked_card_number": "**** **** **** 1111",
                "card_type": "VISA",
                "expiry_month": 12,
                "expiry_year": 2025,
                "status": "ACTIVE",
                "credit_limit": 5000.00,
                "available_credit": 4200.00,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class TransactionResponse(BaseModel):
    """Modelo para respuesta de información de transacción"""
    id: int = Field(..., description="ID único de la transacción")
    transaction_date: datetime = Field(..., description="Fecha y hora de la transacción")
    merchant_name: str = Field(..., description="Nombre del comerciante")
    amount: Decimal = Field(..., description="Monto de la transacción")
    transaction_type: TransactionType = Field(..., description="Tipo de transacción")
    status: TransactionStatus = Field(..., description="Estado de la transacción")
    description: Optional[str] = Field(None, description="Descripción adicional")
    created_at: datetime = Field(..., description="Fecha de creación del registro")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "transaction_date": "2024-01-15T14:30:00Z",
                "merchant_name": "Amazon",
                "amount": 89.99,
                "transaction_type": "PURCHASE",
                "status": "COMPLETED",
                "description": "Online purchase",
                "created_at": "2024-01-15T14:30:00Z"
            }
        }


class TransactionListResponse(BaseModel):
    """Modelo para respuesta de lista de transacciones con paginación"""
    transactions: List[TransactionResponse] = Field(..., description="Lista de transacciones")
    total: int = Field(..., description="Total de transacciones que coinciden con los filtros")
    limit: int = Field(..., description="Límite de resultados por página")
    offset: int = Field(..., description="Número de resultados saltados")
    has_more: bool = Field(..., description="Indica si hay más resultados disponibles")
    
    class Config:
        schema_extra = {
            "example": {
                "transactions": [
                    {
                        "id": 1,
                        "transaction_date": "2024-01-15T14:30:00Z",
                        "merchant_name": "Amazon",
                        "amount": 89.99,
                        "transaction_type": "PURCHASE",
                        "status": "COMPLETED",
                        "description": "Online purchase",
                        "created_at": "2024-01-15T14:30:00Z"
                    }
                ],
                "total": 25,
                "limit": 20,
                "offset": 0,
                "has_more": True
            }
        }


class HealthResponse(BaseModel):
    """Modelo para respuesta de estado de salud"""
    status: str = Field(..., description="Estado general del sistema")
    service: str = Field(..., description="Nombre del servicio")
    version: str = Field(..., description="Versión del servicio")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de la verificación")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "service": "CardDemo API",
                "version": "1.0.0",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class DetailedHealthResponse(BaseModel):
    """Modelo para respuesta detallada de estado de salud"""
    status: str = Field(..., description="Estado general del sistema")
    service: str = Field(..., description="Nombre del servicio")
    version: str = Field(..., description="Versión del servicio")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de la verificación")
    database: dict = Field(..., description="Estado de la base de datos")
    uptime: float = Field(..., description="Tiempo de actividad en segundos")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "service": "CardDemo API",
                "version": "1.0.0",
                "timestamp": "2024-01-15T10:30:00Z",
                "database": {
                    "status": "connected",
                    "response_time_ms": 5.2
                },
                "uptime": 3600.5
            }
        }


class ErrorResponse(BaseModel):
    """Modelo para respuestas de error estandarizadas"""
    error: dict = Field(..., description="Información del error")
    
    class Config:
        schema_extra = {
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Los datos proporcionados no son válidos",
                    "details": [
                        {
                            "field": "email",
                            "message": "El formato del email no es válido"
                        }
                    ],
                    "correlation_id": "req_123456789",
                    "timestamp": "2024-01-15T10:30:00Z"
                }
            }
        }