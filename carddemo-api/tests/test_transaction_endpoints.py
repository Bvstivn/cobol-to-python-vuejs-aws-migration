"""
Tests de integración para endpoints de gestión de transacciones
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from main import app
from database import get_session
from models.database_models import User, Account, CreditCard, Transaction
from services.auth_service import AuthService


# Configurar base de datos de prueba
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user_with_transactions")
def test_user_with_transactions_fixture(session: Session):
    """Crear usuario con cuenta, tarjetas y transacciones de prueba"""
    auth_service = AuthService()
    
    # Crear usuario
    user = User(
        username="transuser",
        email="transuser@example.com",
        hashed_password=auth_service.hash_password("testpassword123"),
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Crear cuenta
    account = Account(
        user_id=user.id,
        account_number="ACC123456",
        first_name="Trans",
        last_name="User"
    )
    session.add(account)
    session.commit()
    session.refresh(account)
    
    # Crear tarjetas
    card1 = CreditCard(
        account_id=account.id,
        card_number="4111111111111111",
        card_type="VISA",
        expiry_month=12,
        expiry_year=2025,
        status="ACTIVE",
        credit_limit=5000.00,
        available_credit=4500.00
    )
    card2 = CreditCard(
        account_id=account.id,
        card_number="5555555555554444",
        card_type="MASTERCARD",
        expiry_month=6,
        expiry_year=2026,
        status="ACTIVE",
        credit_limit=3000.00,
        available_credit=2800.00
    )
    session.add_all([card1, card2])
    session.commit()
    session.refresh(card1)
    session.refresh(card2)
    
    return {"user": user, "account": account, "cards": [card1, card2]}


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client: TestClient, test_user_with_transactions: dict):
    """Obtener headers de autenticación"""
    login_data = {
        "username": "transuser",
        "password": "testpassword123"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestTransactionEndpoints:
    """Tests para endpoints de gestión de transacciones"""
    
    def test_get_my_transactions_creates_sample_transactions_if_none_exist(self, client: TestClient, auth_headers: dict):
        """Test: GET /transactions crea transacciones de ejemplo si no existen"""
        response = client.get("/transactions", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Debe retornar estructura de lista paginada
        assert "transactions" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert "has_more" in data
        
        # Debe tener transacciones de ejemplo
        transactions = data["transactions"]
        assert len(transactions) > 0
        
        # Verificar estructura de transacción
        transaction = transactions[0]
        assert "id" in transaction
        assert "transaction_date" in transaction
        assert "merchant_name" in transaction
        assert "amount" in transaction
        assert "transaction_type" in transaction
        assert "status" in transaction
        assert "created_at" in transaction
    
    def test_get_my_transactions_returns_existing_transactions(self, client: TestClient, auth_headers: dict, session: Session, test_user_with_transactions: dict):
        """Test: GET /transactions retorna transacciones existentes"""
        cards = test_user_with_transactions["cards"]
        
        # Crear transacciones existentes
        transactions = [
            Transaction(
                card_id=cards[0].id,
                transaction_date=datetime.now(timezone.utc) - timedelta(days=1),
                merchant_name="Test Store",
                amount=Decimal("25.50"),
                transaction_type="PURCHASE",
                status="COMPLETED",
                description="Test purchase"
            ),
            Transaction(
                card_id=cards[1].id,
                transaction_date=datetime.now(timezone.utc) - timedelta(days=2),
                merchant_name="Payment Center",
                amount=Decimal("100.00"),
                transaction_type="PAYMENT",
                status="COMPLETED",
                description="Credit card payment"
            )
        ]
        
        for transaction in transactions:
            session.add(transaction)
        session.commit()
        
        response = client.get("/transactions", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] >= 2
        transaction_list = data["transactions"]
        
        # Verificar que las transacciones están ordenadas por fecha descendente
        dates = [t["transaction_date"] for t in transaction_list]
        assert dates == sorted(dates, reverse=True)
        
        # Verificar que contiene nuestras transacciones
        merchant_names = [t["merchant_name"] for t in transaction_list]
        assert "Test Store" in merchant_names
        assert "Payment Center" in merchant_names
    
    def test_get_my_transactions_with_filters(self, client: TestClient, auth_headers: dict, session: Session, test_user_with_transactions: dict):
        """Test: GET /transactions aplica filtros correctamente"""
        cards = test_user_with_transactions["cards"]
        
        # Crear transacciones con diferentes características
        base_date = datetime.now(timezone.utc)
        transactions = [
            Transaction(
                card_id=cards[0].id,
                transaction_date=base_date - timedelta(days=1),
                merchant_name="Amazon",
                amount=Decimal("50.00"),
                transaction_type="PURCHASE",
                status="COMPLETED"
            ),
            Transaction(
                card_id=cards[0].id,
                transaction_date=base_date - timedelta(days=5),
                merchant_name="Starbucks",
                amount=Decimal("5.75"),
                transaction_type="PURCHASE",
                status="COMPLETED"
            ),
            Transaction(
                card_id=cards[1].id,
                transaction_date=base_date - timedelta(days=3),
                merchant_name="Payment",
                amount=Decimal("200.00"),
                transaction_type="PAYMENT",
                status="COMPLETED"
            )
        ]
        
        for transaction in transactions:
            session.add(transaction)
        session.commit()
        
        # Test filtro por tipo de transacción
        response = client.get("/transactions?transaction_type=PURCHASE", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        for transaction in data["transactions"]:
            assert transaction["transaction_type"] == "PURCHASE"
        
        # Test filtro por monto mínimo
        response = client.get("/transactions?min_amount=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        for transaction in data["transactions"]:
            assert float(transaction["amount"]) >= 10.0
        
        # Test filtro por tarjeta específica
        response = client.get(f"/transactions?card_id={cards[0].id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Todas las transacciones deben ser de la tarjeta especificada
        # (No podemos verificar card_id directamente en la respuesta, pero podemos verificar que hay resultados)
        assert len(data["transactions"]) >= 2  # Las dos transacciones de cards[0]
    
    def test_get_my_transactions_pagination(self, client: TestClient, auth_headers: dict, session: Session, test_user_with_transactions: dict):
        """Test: GET /transactions maneja paginación correctamente"""
        cards = test_user_with_transactions["cards"]
        
        # Crear múltiples transacciones
        for i in range(10):
            transaction = Transaction(
                card_id=cards[0].id,
                transaction_date=datetime.now(timezone.utc) - timedelta(days=i),
                merchant_name=f"Store {i}",
                amount=Decimal(f"{10 + i}.00"),
                transaction_type="PURCHASE",
                status="COMPLETED"
            )
            session.add(transaction)
        session.commit()
        
        # Test primera página
        response = client.get("/transactions?limit=5&offset=0", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["transactions"]) == 5
        assert data["limit"] == 5
        assert data["offset"] == 0
        assert data["has_more"] == True
        
        # Test segunda página
        response = client.get("/transactions?limit=5&offset=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["transactions"]) == 5
        assert data["offset"] == 5
    
    def test_get_my_transactions_requires_authentication(self, client: TestClient):
        """Test: GET /transactions requiere autenticación"""
        response = client.get("/transactions")
        assert response.status_code == 401
    
    def test_get_transaction_details_success(self, client: TestClient, auth_headers: dict, session: Session, test_user_with_transactions: dict):
        """Test: GET /transactions/{transaction_id} retorna detalles de transacción específica"""
        cards = test_user_with_transactions["cards"]
        
        # Crear transacción
        transaction = Transaction(
            card_id=cards[0].id,
            transaction_date=datetime.now(timezone.utc),
            merchant_name="Detailed Store",
            amount=Decimal("75.25"),
            transaction_type="PURCHASE",
            status="COMPLETED",
            description="Detailed transaction test"
        )
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        
        response = client.get(f"/transactions/{transaction.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == transaction.id
        assert data["merchant_name"] == "Detailed Store"
        assert float(data["amount"]) == 75.25
        assert data["transaction_type"] == "PURCHASE"
        assert data["status"] == "COMPLETED"
        assert data["description"] == "Detailed transaction test"
    
    def test_get_transaction_details_not_found(self, client: TestClient, auth_headers: dict):
        """Test: GET /transactions/{transaction_id} retorna 404 para transacción inexistente"""
        response = client.get("/transactions/999", headers=auth_headers)
        assert response.status_code == 404
        assert "no encontrada" in response.json()["detail"].lower()
    
    def test_get_transaction_details_requires_authentication(self, client: TestClient):
        """Test: GET /transactions/{transaction_id} requiere autenticación"""
        response = client.get("/transactions/1")
        assert response.status_code == 401
    
    def test_transaction_isolation_between_users(self, client: TestClient, session: Session):
        """Test: Aislamiento de transacciones entre usuarios"""
        auth_service = AuthService()
        
        # Crear dos usuarios con cuentas y tarjetas
        user1 = User(
            username="transuser1",
            email="transuser1@example.com",
            hashed_password=auth_service.hash_password("password123"),
            is_active=True
        )
        user2 = User(
            username="transuser2",
            email="transuser2@example.com",
            hashed_password=auth_service.hash_password("password123"),
            is_active=True
        )
        session.add_all([user1, user2])
        session.commit()
        session.refresh(user1)
        session.refresh(user2)
        
        # Crear cuentas y tarjetas
        account1 = Account(user_id=user1.id, account_number="ACC111", first_name="User", last_name="One")
        account2 = Account(user_id=user2.id, account_number="ACC222", first_name="User", last_name="Two")
        session.add_all([account1, account2])
        session.commit()
        session.refresh(account1)
        session.refresh(account2)
        
        card1 = CreditCard(account_id=account1.id, card_number="4111111111111111", card_type="VISA", expiry_month=12, expiry_year=2025, status="ACTIVE", credit_limit=5000.00, available_credit=4000.00)
        card2 = CreditCard(account_id=account2.id, card_number="5555555555554444", card_type="MASTERCARD", expiry_month=6, expiry_year=2026, status="ACTIVE", credit_limit=3000.00, available_credit=2500.00)
        session.add_all([card1, card2])
        session.commit()
        session.refresh(card1)
        session.refresh(card2)
        
        # Crear transacción para usuario 1
        transaction1 = Transaction(
            card_id=card1.id,
            transaction_date=datetime.now(timezone.utc),
            merchant_name="User1 Store",
            amount=Decimal("100.00"),
            transaction_type="PURCHASE",
            status="COMPLETED"
        )
        session.add(transaction1)
        session.commit()
        session.refresh(transaction1)
        
        # Login usuarios
        headers1 = {"Authorization": f"Bearer {client.post('/auth/login', json={'username': 'transuser1', 'password': 'password123'}).json()['access_token']}"}
        headers2 = {"Authorization": f"Bearer {client.post('/auth/login', json={'username': 'transuser2', 'password': 'password123'}).json()['access_token']}"}
        
        # Usuario 1 puede ver su transacción
        response1 = client.get("/transactions", headers=headers1)
        assert response1.status_code == 200
        transactions1 = response1.json()["transactions"]
        assert len(transactions1) >= 1
        
        # Usuario 2 no puede ver la transacción del usuario 1
        response2 = client.get(f"/transactions/{transaction1.id}", headers=headers2)
        assert response2.status_code == 404
        
        # Usuario 2 no tiene transacciones inicialmente (se crearán de ejemplo)
        response2_list = client.get("/transactions", headers=headers2)
        assert response2_list.status_code == 200
        transactions2 = response2_list.json()["transactions"]
        
        # Verificar que las transacciones son diferentes
        if len(transactions2) > 0:
            transaction_ids_1 = [t["id"] for t in transactions1]
            transaction_ids_2 = [t["id"] for t in transactions2]
            
            # No debe haber IDs en común
            assert not set(transaction_ids_1).intersection(set(transaction_ids_2))