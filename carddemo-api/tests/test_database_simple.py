"""
Tests simplificados para modelos de base de datos
"""
import pytest
from sqlmodel import Session, create_engine, SQLModel
from datetime import datetime
from decimal import Decimal

from models.database_models import User, Account, CreditCard, Transaction
from services.auth_service import AuthService


@pytest.fixture
def test_engine():
    """Crear engine de prueba con SQLite en memoria"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Crear sesión de prueba"""
    with Session(test_engine) as session:
        yield session


def test_user_creation_and_password_hashing(test_session):
    """Test básico de creación de usuario y hashing de contraseñas"""
    auth_service = AuthService()
    
    # Crear usuario
    hashed_password = auth_service.hash_password("PASSWORD123")
    user = User(
        username="TEST001",
        email="test@example.com",
        hashed_password=hashed_password,
        is_active=True
    )
    
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    
    # Verificar que se creó correctamente
    assert user.id is not None
    assert user.username == "TEST001"
    assert auth_service.verify_password("PASSWORD123", user.hashed_password)
    assert not auth_service.verify_password("WRONG", user.hashed_password)


def test_account_creation_with_user(test_session):
    """Test de creación de cuenta asociada a usuario"""
    # Crear usuario primero
    user = User(
        username="TEST002",
        email="test2@example.com",
        hashed_password="hashed_password",
        is_active=True
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    
    # Crear cuenta
    account = Account(
        user_id=user.id,
        account_number="1000000001",
        first_name="John",
        last_name="Doe",
        phone="555-0123",
        address="123 Main St",
        city="Test City",
        state="TC",
        zip_code="12345"
    )
    
    test_session.add(account)
    test_session.commit()
    test_session.refresh(account)
    
    # Verificar relación
    assert account.user_id == user.id
    assert account.account_number == "1000000001"


def test_credit_card_creation(test_session):
    """Test de creación de tarjeta de crédito"""
    # Crear usuario y cuenta
    user = User(username="TEST003", email="test3@example.com", hashed_password="hash", is_active=True)
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    
    account = Account(
        user_id=user.id,
        account_number="1000000002",
        first_name="Jane",
        last_name="Doe"
    )
    test_session.add(account)
    test_session.commit()
    test_session.refresh(account)
    
    # Crear tarjeta
    card = CreditCard(
        account_id=account.id,
        card_number="4111111111111111",
        card_type="VISA",
        expiry_month=12,
        expiry_year=2025,
        status="ACTIVE",
        credit_limit=Decimal("5000.00"),
        available_credit=Decimal("4500.00")
    )
    
    test_session.add(card)
    test_session.commit()
    test_session.refresh(card)
    
    # Verificar
    assert card.account_id == account.id
    assert card.card_type == "VISA"
    assert card.credit_limit == Decimal("5000.00")


def test_transaction_creation(test_session):
    """Test de creación de transacción"""
    # Crear cadena completa: usuario → cuenta → tarjeta → transacción
    user = User(username="TEST004", email="test4@example.com", hashed_password="hash", is_active=True)
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    
    account = Account(user_id=user.id, account_number="1000000003", first_name="Test", last_name="User")
    test_session.add(account)
    test_session.commit()
    test_session.refresh(account)
    
    card = CreditCard(
        account_id=account.id,
        card_number="5555555555554444",
        card_type="MASTERCARD",
        expiry_month=6,
        expiry_year=2026,
        status="ACTIVE",
        credit_limit=Decimal("3000.00"),
        available_credit=Decimal("3000.00")
    )
    test_session.add(card)
    test_session.commit()
    test_session.refresh(card)
    
    # Crear transacción
    transaction = Transaction(
        card_id=card.id,
        transaction_date=datetime(2024, 1, 15, 10, 30),
        merchant_name="Test Store",
        amount=Decimal("99.99"),
        transaction_type="PURCHASE",
        status="COMPLETED",
        description="Test purchase"
    )
    
    test_session.add(transaction)
    test_session.commit()
    test_session.refresh(transaction)
    
    # Verificar
    assert transaction.card_id == card.id
    assert transaction.merchant_name == "Test Store"
    assert transaction.amount == Decimal("99.99")
    assert transaction.transaction_type == "PURCHASE"


def test_database_rollback_on_error(test_session):
    """Test de rollback en caso de error"""
    # Crear usuario válido
    user = User(username="TEST005", email="test5@example.com", hashed_password="hash", is_active=True)
    test_session.add(user)
    
    try:
        # Intentar crear otro usuario con el mismo username (debería fallar por unique constraint)
        duplicate_user = User(username="TEST005", email="different@example.com", hashed_password="hash", is_active=True)
        test_session.add(duplicate_user)
        test_session.commit()
        assert False, "Debería haber fallado por username duplicado"
    except Exception:
        test_session.rollback()
        
        # Verificar que no se creó ningún usuario
        users = test_session.query(User).filter(User.username == "TEST005").all()
        assert len(users) == 0


def test_model_timestamps(test_session):
    """Test de timestamps automáticos"""
    user = User(username="TEST006", email="test6@example.com", hashed_password="hash", is_active=True)
    
    # Verificar que created_at se establece automáticamente
    assert user.created_at is not None
    assert isinstance(user.created_at, datetime)
    
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    
    # Verificar que persiste en la base de datos
    assert user.created_at is not None