"""
Tests unitarios para validación de modelos Pydantic de la API
"""
import pytest
from pydantic import ValidationError
from datetime import datetime, date
from decimal import Decimal

from models.api_models import (
    UserLogin, AccountUpdate, TransactionFilters,
    UserResponse, TokenResponse, AccountResponse, CardResponse,
    TransactionResponse, TransactionListResponse, HealthResponse,
    DetailedHealthResponse, ErrorResponse,
    CardType, CardStatus, TransactionType, TransactionStatus
)


class TestUserLogin:
    """Tests para el modelo UserLogin"""
    
    def test_valid_user_login(self):
        """Test con datos válidos de login"""
        data = {
            "username": "USER0001",
            "password": "PASSWORD123"
        }
        user_login = UserLogin(**data)
        assert user_login.username == "USER0001"
        assert user_login.password == "PASSWORD123"
    
    def test_username_too_short(self):
        """Test con username demasiado corto"""
        data = {
            "username": "AB",  # Menos de 3 caracteres
            "password": "PASSWORD123"
        }
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(**data)
        assert "at least 3 characters" in str(exc_info.value)
    
    def test_username_too_long(self):
        """Test con username demasiado largo"""
        data = {
            "username": "A" * 51,  # Más de 50 caracteres
            "password": "PASSWORD123"
        }
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(**data)
        assert "at most 50 characters" in str(exc_info.value)
    
    def test_password_too_short(self):
        """Test con password demasiado corto"""
        data = {
            "username": "USER0001",
            "password": "1234567"  # Menos de 8 caracteres
        }
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(**data)
        assert "at least 8 characters" in str(exc_info.value)
    
    def test_missing_fields(self):
        """Test con campos faltantes"""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(username="USER0001")  # Falta password
        assert "password" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(password="PASSWORD123")  # Falta username
        assert "username" in str(exc_info.value)


class TestAccountUpdate:
    """Tests para el modelo AccountUpdate"""
    
    def test_valid_account_update(self):
        """Test con datos válidos de actualización"""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "phone": "555-123-4567",  # Teléfono con suficientes dígitos
            "address": "123 Main St",
            "city": "Anytown",
            "state": "ca",  # Debe convertirse a mayúsculas
            "zip_code": "12345"
        }
        account_update = AccountUpdate(**data)
        assert account_update.first_name == "John"
        assert account_update.state == "CA"  # Convertido a mayúsculas
    
    def test_optional_fields(self):
        """Test con campos opcionales"""
        data = {
            "first_name": "John"
        }
        account_update = AccountUpdate(**data)
        assert account_update.first_name == "John"
        assert account_update.last_name is None
        assert account_update.phone is None
    
    def test_phone_validation(self):
        """Test de validación de teléfono"""
        # Teléfono válido
        data = {"phone": "555-123-4567"}
        account_update = AccountUpdate(**data)
        assert account_update.phone == "555-123-4567"
        
        # Teléfono con pocos dígitos
        data = {"phone": "123"}
        with pytest.raises(ValidationError) as exc_info:
            AccountUpdate(**data)
        assert "al menos 10 dígitos" in str(exc_info.value)
    
    def test_state_validation(self):
        """Test de validación de estado"""
        data = {"state": "ca"}
        account_update = AccountUpdate(**data)
        assert account_update.state == "CA"
    
    def test_field_length_validation(self):
        """Test de validación de longitud de campos"""
        # Nombre demasiado largo
        data = {"first_name": "A" * 51}
        with pytest.raises(ValidationError) as exc_info:
            AccountUpdate(**data)
        assert "at most 50 characters" in str(exc_info.value)
        
        # Dirección demasiado larga
        data = {"address": "A" * 201}
        with pytest.raises(ValidationError) as exc_info:
            AccountUpdate(**data)
        assert "at most 200 characters" in str(exc_info.value)


class TestTransactionFilters:
    """Tests para el modelo TransactionFilters"""
    
    def test_valid_filters(self):
        """Test con filtros válidos"""
        data = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "card_id": 1,
            "transaction_type": "PURCHASE",
            "min_amount": 10.00,
            "max_amount": 1000.00,
            "limit": 20,
            "offset": 0
        }
        filters = TransactionFilters(**data)
        assert filters.start_date == date(2024, 1, 1)
        assert filters.end_date == date(2024, 1, 31)
        assert filters.transaction_type == TransactionType.PURCHASE
    
    def test_default_values(self):
        """Test de valores por defecto"""
        filters = TransactionFilters()
        assert filters.limit == 50
        assert filters.offset == 0
        assert filters.start_date is None
    
    def test_date_range_validation(self):
        """Test de validación de rango de fechas"""
        data = {
            "start_date": "2024-01-31",
            "end_date": "2024-01-01"  # Fecha de fin anterior a inicio
        }
        with pytest.raises(ValidationError) as exc_info:
            TransactionFilters(**data)
        assert "posterior a la fecha de inicio" in str(exc_info.value)
    
    def test_amount_range_validation(self):
        """Test de validación de rango de montos"""
        data = {
            "min_amount": 1000.00,
            "max_amount": 100.00  # Monto máximo menor al mínimo
        }
        with pytest.raises(ValidationError) as exc_info:
            TransactionFilters(**data)
        assert "mayor al monto mínimo" in str(exc_info.value)
    
    def test_limit_validation(self):
        """Test de validación de límite"""
        # Límite demasiado alto
        data = {"limit": 101}
        with pytest.raises(ValidationError) as exc_info:
            TransactionFilters(**data)
        assert "less than or equal to 100" in str(exc_info.value)
        
        # Límite demasiado bajo
        data = {"limit": 0}
        with pytest.raises(ValidationError) as exc_info:
            TransactionFilters(**data)
        assert "greater than or equal to 1" in str(exc_info.value)
    
    def test_negative_offset(self):
        """Test con offset negativo"""
        data = {"offset": -1}
        with pytest.raises(ValidationError) as exc_info:
            TransactionFilters(**data)
        assert "greater than or equal to 0" in str(exc_info.value)


class TestResponseModels:
    """Tests para modelos de respuesta"""
    
    def test_user_response(self):
        """Test del modelo UserResponse"""
        data = {
            "id": 1,
            "username": "USER0001",
            "email": "user@carddemo.com",
            "is_active": True
        }
        user_response = UserResponse(**data)
        assert user_response.id == 1
        assert user_response.username == "USER0001"
        assert user_response.is_active is True
    
    def test_token_response(self):
        """Test del modelo TokenResponse"""
        user_data = {
            "id": 1,
            "username": "USER0001",
            "email": "user@carddemo.com",
            "is_active": True
        }
        data = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
            "token_type": "bearer",
            "expires_in": 1800,
            "user": user_data
        }
        token_response = TokenResponse(**data)
        assert token_response.access_token.startswith("eyJ")
        assert token_response.token_type == "bearer"
        assert token_response.expires_in == 1800
        assert token_response.user.username == "USER0001"
    
    def test_account_response(self):
        """Test del modelo AccountResponse"""
        data = {
            "id": 1,
            "account_number": "1000000001",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "555-0123",
            "address": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip_code": "12345",
            "created_at": datetime(2024, 1, 15, 10, 30),
            "updated_at": None
        }
        account_response = AccountResponse(**data)
        assert account_response.account_number == "1000000001"
        assert account_response.first_name == "John"
        assert account_response.updated_at is None
    
    def test_card_response(self):
        """Test del modelo CardResponse"""
        data = {
            "id": 1,
            "masked_card_number": "**** **** **** 1111",
            "card_type": "VISA",
            "expiry_month": 12,
            "expiry_year": 2025,
            "status": "ACTIVE",
            "credit_limit": Decimal("5000.00"),
            "available_credit": Decimal("4200.00"),
            "created_at": datetime(2024, 1, 15, 10, 30)
        }
        card_response = CardResponse(**data)
        assert card_response.card_type == CardType.VISA
        assert card_response.status == CardStatus.ACTIVE
        assert card_response.credit_limit == Decimal("5000.00")
    
    def test_transaction_response(self):
        """Test del modelo TransactionResponse"""
        data = {
            "id": 1,
            "transaction_date": datetime(2024, 1, 15, 14, 30),
            "merchant_name": "Amazon",
            "amount": Decimal("89.99"),
            "transaction_type": "PURCHASE",
            "status": "COMPLETED",
            "description": "Online purchase",
            "created_at": datetime(2024, 1, 15, 14, 30)
        }
        transaction_response = TransactionResponse(**data)
        assert transaction_response.merchant_name == "Amazon"
        assert transaction_response.transaction_type == TransactionType.PURCHASE
        assert transaction_response.status == TransactionStatus.COMPLETED
        assert transaction_response.amount == Decimal("89.99")
    
    def test_transaction_list_response(self):
        """Test del modelo TransactionListResponse"""
        transaction_data = {
            "id": 1,
            "transaction_date": datetime(2024, 1, 15, 14, 30),
            "merchant_name": "Amazon",
            "amount": Decimal("89.99"),
            "transaction_type": "PURCHASE",
            "status": "COMPLETED",
            "description": "Online purchase",
            "created_at": datetime(2024, 1, 15, 14, 30)
        }
        data = {
            "transactions": [transaction_data],
            "total": 25,
            "limit": 20,
            "offset": 0,
            "has_more": True
        }
        list_response = TransactionListResponse(**data)
        assert len(list_response.transactions) == 1
        assert list_response.total == 25
        assert list_response.has_more is True
    
    def test_health_response(self):
        """Test del modelo HealthResponse"""
        data = {
            "status": "healthy",
            "service": "CardDemo API",
            "version": "1.0.0"
        }
        health_response = HealthResponse(**data)
        assert health_response.status == "healthy"
        assert health_response.service == "CardDemo API"
        assert isinstance(health_response.timestamp, datetime)
    
    def test_detailed_health_response(self):
        """Test del modelo DetailedHealthResponse"""
        data = {
            "status": "healthy",
            "service": "CardDemo API",
            "version": "1.0.0",
            "database": {
                "status": "connected",
                "response_time_ms": 5.2
            },
            "uptime": 3600.5
        }
        detailed_health = DetailedHealthResponse(**data)
        assert detailed_health.database["status"] == "connected"
        assert detailed_health.uptime == 3600.5


class TestEnums:
    """Tests para enums utilizados en los modelos"""
    
    def test_card_type_enum(self):
        """Test del enum CardType"""
        assert CardType.VISA == "VISA"
        assert CardType.MASTERCARD == "MASTERCARD"
        assert CardType.AMEX == "AMEX"
        assert CardType.DISCOVER == "DISCOVER"
    
    def test_card_status_enum(self):
        """Test del enum CardStatus"""
        assert CardStatus.ACTIVE == "ACTIVE"
        assert CardStatus.BLOCKED == "BLOCKED"
        assert CardStatus.EXPIRED == "EXPIRED"
    
    def test_transaction_type_enum(self):
        """Test del enum TransactionType"""
        assert TransactionType.PURCHASE == "PURCHASE"
        assert TransactionType.PAYMENT == "PAYMENT"
        assert TransactionType.REFUND == "REFUND"
    
    def test_transaction_status_enum(self):
        """Test del enum TransactionStatus"""
        assert TransactionStatus.PENDING == "PENDING"
        assert TransactionStatus.COMPLETED == "COMPLETED"
        assert TransactionStatus.FAILED == "FAILED"


class TestValidationEdgeCases:
    """Tests para casos límite de validación"""
    
    def test_decimal_precision(self):
        """Test de precisión de decimales"""
        data = {
            "id": 1,
            "masked_card_number": "**** **** **** 1111",
            "card_type": "VISA",
            "expiry_month": 12,
            "expiry_year": 2025,
            "status": "ACTIVE",
            "credit_limit": Decimal("5000.123"),  # Más de 2 decimales
            "available_credit": Decimal("4200.00"),
            "created_at": datetime(2024, 1, 15, 10, 30)
        }
        # Debería aceptar el valor aunque tenga más decimales
        card_response = CardResponse(**data)
        assert card_response.credit_limit == Decimal("5000.123")
    
    def test_empty_optional_fields(self):
        """Test con campos opcionales vacíos"""
        data = {
            "first_name": "",  # String vacío
            "phone": None,     # Valor None
        }
        # String vacío debería fallar validación de min_length
        with pytest.raises(ValidationError):
            AccountUpdate(**data)
    
    def test_boundary_values(self):
        """Test con valores en los límites"""
        # Mes de expiración en límites
        data = {
            "id": 1,
            "masked_card_number": "**** **** **** 1111",
            "card_type": "VISA",
            "expiry_month": 1,  # Límite inferior
            "expiry_year": 2024,  # Límite inferior
            "status": "ACTIVE",
            "credit_limit": Decimal("0.01"),  # Valor mínimo
            "available_credit": Decimal("0.00"),
            "created_at": datetime(2024, 1, 15, 10, 30)
        }
        card_response = CardResponse(**data)
        assert card_response.expiry_month == 1
        
        # Mes de expiración en límite superior
        data["expiry_month"] = 12
        card_response = CardResponse(**data)
        assert card_response.expiry_month == 12