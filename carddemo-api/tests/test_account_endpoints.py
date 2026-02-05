"""
Tests de integración para endpoints de gestión de cuentas
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from main import app
from database import get_session
from models.database_models import User, Account
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


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Crear usuario de prueba"""
    auth_service = AuthService()
    hashed_password = auth_service.hash_password("testpassword123")
    
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_password,
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client: TestClient, test_user: User):
    """Obtener headers de autenticación"""
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestAccountEndpoints:
    """Tests para endpoints de gestión de cuentas"""
    
    def test_get_my_account_creates_account_if_not_exists(self, client: TestClient, auth_headers: dict):
        """Test: GET /accounts/me crea cuenta si no existe"""
        response = client.get("/accounts/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura de respuesta
        assert "id" in data
        assert "account_number" in data
        assert "first_name" in data
        assert "last_name" in data
        assert "created_at" in data
        
        # Verificar que se creó una cuenta básica
        assert data["first_name"] == ""
        assert data["last_name"] == ""
        assert data["account_number"].startswith("ACC")
    
    def test_get_my_account_returns_existing_account(self, client: TestClient, auth_headers: dict, session: Session, test_user: User):
        """Test: GET /accounts/me retorna cuenta existente"""
        # Crear cuenta existente
        account = Account(
            user_id=test_user.id,
            account_number="ACC123456",
            first_name="John",
            last_name="Doe",
            phone="555-0123",
            address="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="12345"
        )
        session.add(account)
        session.commit()
        
        response = client.get("/accounts/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["account_number"] == "ACC123456"
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["phone"] == "555-0123"
        assert data["address"] == "123 Main St"
        assert data["city"] == "Anytown"
        assert data["state"] == "CA"
        assert data["zip_code"] == "12345"
    
    def test_get_my_account_requires_authentication(self, client: TestClient):
        """Test: GET /accounts/me requiere autenticación"""
        response = client.get("/accounts/me")
        assert response.status_code == 401
    
    def test_update_my_account_success(self, client: TestClient, auth_headers: dict):
        """Test: PUT /accounts/me actualiza cuenta exitosamente"""
        update_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "phone": "555-987-6543",  # Teléfono con 10 dígitos
            "address": "456 Oak Ave",
            "city": "Newtown",
            "state": "NY",
            "zip_code": "54321"
        }
        
        response = client.put("/accounts/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Smith"
        assert data["phone"] == "555-987-6543"
        assert data["address"] == "456 Oak Ave"
        assert data["city"] == "Newtown"
        assert data["state"] == "NY"
        assert data["zip_code"] == "54321"
        assert data["updated_at"] is not None
    
    def test_update_my_account_partial_update(self, client: TestClient, auth_headers: dict):
        """Test: PUT /accounts/me permite actualización parcial"""
        # Primero crear cuenta con datos iniciales
        initial_data = {
            "first_name": "John",
            "last_name": "Doe",
            "phone": "555-012-3456"  # Teléfono con 10 dígitos
        }
        client.put("/accounts/me", json=initial_data, headers=auth_headers)
        
        # Actualizar solo algunos campos
        update_data = {
            "first_name": "Johnny",
            "city": "New City"
        }
        
        response = client.put("/accounts/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que se actualizaron los campos especificados
        assert data["first_name"] == "Johnny"
        assert data["city"] == "New City"
        
        # Verificar que se mantuvieron los campos no especificados
        assert data["last_name"] == "Doe"
        assert data["phone"] == "555-012-3456"
    
    def test_update_my_account_requires_authentication(self, client: TestClient):
        """Test: PUT /accounts/me requiere autenticación"""
        update_data = {"first_name": "Test"}
        response = client.put("/accounts/me", json=update_data)
        assert response.status_code == 401
    
    def test_update_my_account_validates_phone(self, client: TestClient, auth_headers: dict):
        """Test: PUT /accounts/me valida formato de teléfono"""
        update_data = {
            "phone": "123"  # Teléfono muy corto
        }
        
        response = client.put("/accounts/me", json=update_data, headers=auth_headers)
        assert response.status_code == 422  # Validation error
    
    def test_update_my_account_validates_state(self, client: TestClient, auth_headers: dict):
        """Test: PUT /accounts/me valida estado"""
        update_data = {
            "state": "ca"  # Debe convertirse a mayúsculas
        }
        
        response = client.put("/accounts/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["state"] == "CA"
    
    def test_account_isolation_between_users(self, client: TestClient, session: Session):
        """Test: Aislamiento de datos entre usuarios"""
        # Crear dos usuarios
        auth_service = AuthService()
        
        # Usuario 1
        user1 = User(
            username="user1",
            email="user1@example.com",
            hashed_password=auth_service.hash_password("password123"),
            is_active=True
        )
        session.add(user1)
        
        # Usuario 2
        user2 = User(
            username="user2",
            email="user2@example.com",
            hashed_password=auth_service.hash_password("password123"),
            is_active=True
        )
        session.add(user2)
        session.commit()
        
        # Login usuario 1
        response1 = client.post("/auth/login", json={"username": "user1", "password": "password123"})
        token1 = response1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}
        
        # Login usuario 2
        response2 = client.post("/auth/login", json={"username": "user2", "password": "password123"})
        token2 = response2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Usuario 1 actualiza su cuenta
        client.put("/accounts/me", json={"first_name": "User", "last_name": "One"}, headers=headers1)
        
        # Usuario 2 actualiza su cuenta
        client.put("/accounts/me", json={"first_name": "User", "last_name": "Two"}, headers=headers2)
        
        # Verificar que cada usuario ve solo su cuenta
        account1 = client.get("/accounts/me", headers=headers1).json()
        account2 = client.get("/accounts/me", headers=headers2).json()
        
        assert account1["last_name"] == "One"
        assert account2["last_name"] == "Two"
        assert account1["id"] != account2["id"]
        assert account1["account_number"] != account2["account_number"]