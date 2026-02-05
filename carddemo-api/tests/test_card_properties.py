"""
Tests de propiedades para gestión de tarjetas de crédito (versión simplificada)
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


@pytest.fixture(name="test_users_with_cards")
def test_users_with_cards_fixture(session: Session):
    """Crear múltiples usuarios con cuentas y tarjetas de prueba"""
    auth_service = AuthService()
    users_data = []
    
    for i in range(3):
        # Crear usuario
        user = User(
            username=f"carduser{i}",
            email=f"carduser{i}@example.com",
            hashed_password=auth_service.hash_password("testpassword123"),
            is_active=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Crear cuenta
        account = Account(
            user_id=user.id,
            account_number=f"ACC{i:06d}",
            first_name=f"Card{i}",
            last_name=f"User{i}"
        )
        session.add(account)
        session.commit()
        session.refresh(account)
        
        users_data.append({"user": user, "account": account})
    
    return users_data


def get_auth_headers(client: TestClient, username: str) -> dict:
    """Obtener headers de autenticación para un usuario"""
    login_data = {
        "username": username,
        "password": "testpassword123"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestCardProperties:
    """Tests de propiedades para gestión de tarjetas de crédito"""
    
    def test_property_10_complete_card_listing(self, client: TestClient, test_users_with_cards: list, session: Session):
        """
        **Propiedad 10: Listado completo de tarjetas de usuario**
        **Valida: Requisitos 3.1**
        
        Verifica que un usuario puede obtener todas sus tarjetas de crédito
        """
        user_data = test_users_with_cards[0]
        account = user_data["account"]
        headers = get_auth_headers(client, "carduser0")
        
        # Crear múltiples tarjetas para el usuario
        cards = [
            CreditCard(
                account_id=account.id,
                card_number="4111111111111111",
                card_type="VISA",
                expiry_month=12,
                expiry_year=2025,
                status="ACTIVE",
                credit_limit=5000.00,
                available_credit=4500.00
            ),
            CreditCard(
                account_id=account.id,
                card_number="5555555555554444",
                card_type="MASTERCARD",
                expiry_month=6,
                expiry_year=2026,
                status="ACTIVE",
                credit_limit=3000.00,
                available_credit=2800.00
            )
        ]
        
        for card in cards:
            session.add(card)
        session.commit()
        
        # Obtener lista de tarjetas
        response = client.get("/cards", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que se retornan todas las tarjetas
        assert len(data) == 2
        
        # Verificar que cada tarjeta tiene la estructura correcta
        for card_data in data:
            assert "id" in card_data
            assert "masked_card_number" in card_data
            assert "card_type" in card_data
            assert "expiry_month" in card_data
            assert "expiry_year" in card_data
            assert "status" in card_data
            assert "credit_limit" in card_data
            assert "available_credit" in card_data
            assert "created_at" in card_data
        
        # Verificar tipos de tarjeta
        card_types = [card["card_type"] for card in data]
        assert "VISA" in card_types
        assert "MASTERCARD" in card_types
    
    def test_property_11_card_number_masking(self, client: TestClient, test_users_with_cards: list, session: Session):
        """
        **Propiedad 11: Enmascaramiento de números de tarjeta**
        **Valida: Requisitos 3.2**
        
        Verifica que los números de tarjeta se enmascaran correctamente en las respuestas
        """
        user_data = test_users_with_cards[1]
        account = user_data["account"]
        headers = get_auth_headers(client, "carduser1")
        
        # Crear tarjetas con diferentes números
        test_cards = [
            ("4111111111111111", "**** **** **** 1111"),
            ("5555555555554444", "**** **** **** 4444"),
            ("378282246310005", "**** **** **** 0005"),
            ("6011111111111117", "**** **** **** 1117")
        ]
        
        created_cards = []
        for card_number, expected_masked in test_cards:
            card = CreditCard(
                account_id=account.id,
                card_number=card_number,
                card_type="VISA",
                expiry_month=12,
                expiry_year=2025,
                status="ACTIVE",
                credit_limit=1000.00,
                available_credit=900.00
            )
            session.add(card)
            created_cards.append((card, expected_masked))
        
        session.commit()
        
        # Verificar enmascaramiento en lista de tarjetas
        response = client.get("/cards", headers=headers)
        assert response.status_code == 200
        cards_data = response.json()
        
        # Verificar que todos los números están enmascarados correctamente
        for i, (card, expected_masked) in enumerate(created_cards):
            session.refresh(card)
            card_data = next(c for c in cards_data if c["id"] == card.id)
            
            # Verificar formato de enmascaramiento
            assert card_data["masked_card_number"] == expected_masked
            assert card_data["masked_card_number"].startswith("**** **** ****")
            assert len(card_data["masked_card_number"]) == 19
            
            # Verificar que el número original no aparece en la respuesta
            response_str = str(card_data)
            assert card.card_number not in response_str
        
        # Verificar enmascaramiento en detalles de tarjeta individual
        for card, expected_masked in created_cards:
            response = client.get(f"/cards/{card.id}", headers=headers)
            assert response.status_code == 200
            card_detail = response.json()
            
            assert card_detail["masked_card_number"] == expected_masked
            # Verificar que el número completo no se filtra
            response_str = str(card_detail)
            assert card.card_number not in response_str
    
    def test_property_no_cards_case(self, client: TestClient, test_users_with_cards: list):
        """
        Test unitario para casos sin tarjetas
        **Valida: Requisitos 3.3**
        
        Verifica el comportamiento cuando un usuario no tiene tarjetas asociadas
        """
        headers = get_auth_headers(client, "carduser2")
        
        # Usuario sin tarjetas - debe crear tarjetas de ejemplo
        response = client.get("/cards", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Se deben crear tarjetas de ejemplo automáticamente
        assert len(data) == 2  # Se crean 2 tarjetas de ejemplo
        
        # Verificar que las tarjetas de ejemplo tienen estructura válida
        for card in data:
            assert card["masked_card_number"].startswith("**** **** ****")
            assert card["card_type"] in ["VISA", "MASTERCARD"]
            assert card["status"] == "ACTIVE"
            assert float(card["credit_limit"]) > 0
            assert float(card["available_credit"]) > 0
            assert card["expiry_year"] >= 2025
            assert 1 <= card["expiry_month"] <= 12