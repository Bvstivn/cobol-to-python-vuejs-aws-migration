"""
Tests de integración para endpoints de gestión de tarjetas de crédito
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from main import app
from database import get_session
from models.database_models import User, Account, CreditCard
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


@pytest.fixture(name="test_user_with_cards")
def test_user_with_cards_fixture(session: Session):
    """Crear usuario con cuenta y tarjetas de prueba"""
    auth_service = AuthService()
    
    # Crear usuario
    user = User(
        username="carduser",
        email="carduser@example.com",
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
        first_name="Card",
        last_name="User"
    )
    session.add(account)
    session.commit()
    session.refresh(account)
    
    return {"user": user, "account": account}


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client: TestClient, test_user_with_cards: dict):
    """Obtener headers de autenticación"""
    login_data = {
        "username": "carduser",
        "password": "testpassword123"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestCardEndpoints:
    """Tests para endpoints de gestión de tarjetas"""
    
    def test_get_my_cards_creates_sample_cards_if_none_exist(self, client: TestClient, auth_headers: dict):
        """Test: GET /cards crea tarjetas de ejemplo si no existen"""
        response = client.get("/cards", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Debe retornar lista de tarjetas
        assert isinstance(data, list)
        assert len(data) == 2  # Se crean 2 tarjetas de ejemplo
        
        # Verificar estructura de respuesta
        card = data[0]
        assert "id" in card
        assert "masked_card_number" in card
        assert "card_type" in card
        assert "expiry_month" in card
        assert "expiry_year" in card
        assert "status" in card
        assert "credit_limit" in card
        assert "available_credit" in card
        assert "created_at" in card
        
        # Verificar que el número está enmascarado
        assert card["masked_card_number"].startswith("**** **** ****")
        assert len(card["masked_card_number"]) == 19  # "**** **** **** 1234"
    
    def test_get_my_cards_returns_existing_cards(self, client: TestClient, auth_headers: dict, session: Session, test_user_with_cards: dict):
        """Test: GET /cards retorna tarjetas existentes"""
        account = test_user_with_cards["account"]
        
        # Crear tarjeta existente
        card = CreditCard(
            account_id=account.id,
            card_number="4111111111111111",
            card_type="VISA",
            expiry_month=6,
            expiry_year=2027,
            status="ACTIVE",
            credit_limit=10000.00,
            available_credit=8500.00
        )
        session.add(card)
        session.commit()
        
        response = client.get("/cards", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 1
        card_data = data[0]
        
        assert card_data["masked_card_number"] == "**** **** **** 1111"
        assert card_data["card_type"] == "VISA"
        assert card_data["expiry_month"] == 6
        assert card_data["expiry_year"] == 2027
        assert card_data["status"] == "ACTIVE"
        assert float(card_data["credit_limit"]) == 10000.00
        assert float(card_data["available_credit"]) == 8500.00
    
    def test_get_my_cards_requires_authentication(self, client: TestClient):
        """Test: GET /cards requiere autenticación"""
        response = client.get("/cards")
        assert response.status_code == 401
    
    def test_get_card_details_success(self, client: TestClient, auth_headers: dict, session: Session, test_user_with_cards: dict):
        """Test: GET /cards/{card_id} retorna detalles de tarjeta específica"""
        account = test_user_with_cards["account"]
        
        # Crear tarjeta
        card = CreditCard(
            account_id=account.id,
            card_number="5555555555554444",
            card_type="MASTERCARD",
            expiry_month=9,
            expiry_year=2028,
            status="ACTIVE",
            credit_limit=7500.00,
            available_credit=6200.00
        )
        session.add(card)
        session.commit()
        session.refresh(card)
        
        response = client.get(f"/cards/{card.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == card.id
        assert data["masked_card_number"] == "**** **** **** 4444"
        assert data["card_type"] == "MASTERCARD"
        assert data["expiry_month"] == 9
        assert data["expiry_year"] == 2028
        assert data["status"] == "ACTIVE"
        assert float(data["credit_limit"]) == 7500.00
        assert float(data["available_credit"]) == 6200.00
    
    def test_get_card_details_not_found(self, client: TestClient, auth_headers: dict):
        """Test: GET /cards/{card_id} retorna 404 para tarjeta inexistente"""
        response = client.get("/cards/999", headers=auth_headers)
        assert response.status_code == 404
        assert "no encontrada" in response.json()["detail"].lower()
    
    def test_get_card_details_requires_authentication(self, client: TestClient):
        """Test: GET /cards/{card_id} requiere autenticación"""
        response = client.get("/cards/1")
        assert response.status_code == 401
    
    def test_card_isolation_between_users(self, client: TestClient, session: Session):
        """Test: Aislamiento de tarjetas entre usuarios"""
        auth_service = AuthService()
        
        # Crear dos usuarios con cuentas
        user1 = User(
            username="carduser1",
            email="carduser1@example.com",
            hashed_password=auth_service.hash_password("password123"),
            is_active=True
        )
        user2 = User(
            username="carduser2", 
            email="carduser2@example.com",
            hashed_password=auth_service.hash_password("password123"),
            is_active=True
        )
        session.add_all([user1, user2])
        session.commit()
        session.refresh(user1)
        session.refresh(user2)
        
        # Crear cuentas
        account1 = Account(user_id=user1.id, account_number="ACC111", first_name="User", last_name="One")
        account2 = Account(user_id=user2.id, account_number="ACC222", first_name="User", last_name="Two")
        session.add_all([account1, account2])
        session.commit()
        session.refresh(account1)
        session.refresh(account2)
        
        # Crear tarjeta para usuario 1
        card1 = CreditCard(
            account_id=account1.id,
            card_number="4111111111111111",
            card_type="VISA",
            expiry_month=12,
            expiry_year=2025,
            status="ACTIVE",
            credit_limit=5000.00,
            available_credit=4000.00
        )
        session.add(card1)
        session.commit()
        session.refresh(card1)
        
        # Login usuarios
        headers1 = {"Authorization": f"Bearer {client.post('/auth/login', json={'username': 'carduser1', 'password': 'password123'}).json()['access_token']}"}
        headers2 = {"Authorization": f"Bearer {client.post('/auth/login', json={'username': 'carduser2', 'password': 'password123'}).json()['access_token']}"}
        
        # Usuario 1 puede ver su tarjeta
        response1 = client.get("/cards", headers=headers1)
        assert response1.status_code == 200
        cards1 = response1.json()
        assert len(cards1) == 1
        
        # Usuario 2 no puede ver la tarjeta del usuario 1
        response2 = client.get(f"/cards/{card1.id}", headers=headers2)
        assert response2.status_code == 404
        
        # Usuario 2 no tiene tarjetas (se crearán de ejemplo)
        response2_list = client.get("/cards", headers=headers2)
        assert response2_list.status_code == 200
        cards2 = response2_list.json()
        assert len(cards2) == 2  # Tarjetas de ejemplo creadas
        
        # Verificar que las tarjetas son diferentes
        assert cards1[0]["id"] != cards2[0]["id"]
        assert cards1[0]["id"] != cards2[1]["id"]