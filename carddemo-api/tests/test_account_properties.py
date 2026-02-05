"""
Tests de propiedades para gestión de cuentas (versión simplificada)
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


@pytest.fixture(name="test_users")
def test_users_fixture(session: Session):
    """Crear múltiples usuarios de prueba"""
    auth_service = AuthService()
    users = []
    
    for i in range(3):
        user = User(
            username=f"testuser{i}",
            email=f"test{i}@example.com",
            hashed_password=auth_service.hash_password("testpassword123"),
            is_active=True
        )
        session.add(user)
        users.append(user)
    
    session.commit()
    for user in users:
        session.refresh(user)
    
    return users


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


class TestAccountProperties:
    """Tests de propiedades para gestión de cuentas"""
    
    def test_property_6_access_to_own_account_info(self, client: TestClient, test_users: list):
        """
        **Propiedad 6: Acceso a información de cuenta propia**
        **Valida: Requisitos 2.1**
        
        Verifica que un usuario autenticado puede acceder a su propia información de cuenta
        """
        # Obtener headers de autenticación para el primer usuario
        headers = get_auth_headers(client, "testuser0")
        
        # Acceder a información de cuenta propia
        response = client.get("/accounts/me", headers=headers)
        
        # Verificar que el acceso es exitoso
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que se retorna información de cuenta
        assert "id" in data
        assert "account_number" in data
        assert "first_name" in data
        assert "last_name" in data
        assert "created_at" in data
        
        # Verificar que el número de cuenta es único y válido
        assert data["account_number"].startswith("ACC")
        assert len(data["account_number"]) > 3
    
    def test_property_7_persistence_of_valid_updates(self, client: TestClient, test_users: list):
        """
        **Propiedad 7: Persistencia de actualizaciones de cuenta válidas**
        **Valida: Requisitos 2.2**
        
        Verifica que las actualizaciones válidas de cuenta se persisten correctamente
        """
        headers = get_auth_headers(client, "testuser1")
        
        # Datos de actualización válidos
        update_data = {
            "first_name": "John",
            "last_name": "Doe",
            "phone": "555-123-4567",
            "city": "Test City"
        }
        
        # Actualizar cuenta
        response = client.put("/accounts/me", json=update_data, headers=headers)
        assert response.status_code == 200
        
        # Verificar que los datos se actualizaron
        updated_data = response.json()
        assert updated_data["first_name"] == "John"
        assert updated_data["last_name"] == "Doe"
        assert updated_data["phone"] == "555-123-4567"
        assert updated_data["city"] == "Test City"
        assert updated_data["updated_at"] is not None
        
        # Verificar persistencia obteniendo la cuenta nuevamente
        response = client.get("/accounts/me", headers=headers)
        assert response.status_code == 200
        persisted_data = response.json()
        
        # Los datos deben ser los mismos
        assert persisted_data["first_name"] == "John"
        assert persisted_data["last_name"] == "Doe"
        assert persisted_data["phone"] == "555-123-4567"
        assert persisted_data["city"] == "Test City"
    
    def test_property_8_data_isolation_between_users(self, client: TestClient, test_users: list):
        """
        **Propiedad 8: Aislamiento de datos entre usuarios**
        **Valida: Requisitos 2.4, 3.5, 4.5**
        
        Verifica que los usuarios solo pueden acceder a sus propios datos
        """
        # Obtener headers para dos usuarios diferentes
        headers1 = get_auth_headers(client, "testuser0")
        headers2 = get_auth_headers(client, "testuser1")
        
        # Usuario 1 actualiza su cuenta
        update_data1 = {
            "first_name": "User",
            "last_name": "One",
            "city": "City One"
        }
        response1 = client.put("/accounts/me", json=update_data1, headers=headers1)
        assert response1.status_code == 200
        
        # Usuario 2 actualiza su cuenta
        update_data2 = {
            "first_name": "User",
            "last_name": "Two", 
            "city": "City Two"
        }
        response2 = client.put("/accounts/me", json=update_data2, headers=headers2)
        assert response2.status_code == 200
        
        # Verificar que cada usuario ve solo sus propios datos
        account1 = client.get("/accounts/me", headers=headers1).json()
        account2 = client.get("/accounts/me", headers=headers2).json()
        
        # Los datos deben ser diferentes
        assert account1["last_name"] == "One"
        assert account2["last_name"] == "Two"
        assert account1["city"] == "City One"
        assert account2["city"] == "City Two"
        
        # Los IDs y números de cuenta deben ser diferentes
        assert account1["id"] != account2["id"]
        assert account1["account_number"] != account2["account_number"]
        
        # Verificar que no hay contaminación cruzada de datos
        assert account1["last_name"] != account2["last_name"]
        assert account1["city"] != account2["city"]
    
    def test_property_9_audit_trail_of_account_changes(self, client: TestClient, test_users: list):
        """
        **Propiedad 9: Auditoría de cambios de cuenta**
        **Valida: Requisitos 2.5**
        
        Verifica que los cambios de cuenta mantienen un rastro de auditoría básico
        """
        headers = get_auth_headers(client, "testuser2")
        
        # Obtener cuenta inicial
        initial_response = client.get("/accounts/me", headers=headers)
        assert initial_response.status_code == 200
        initial_data = initial_response.json()
        initial_created_at = initial_data["created_at"]
        initial_updated_at = initial_data["updated_at"]
        
        # Realizar actualización
        update_data = {
            "first_name": "Updated",
            "last_name": "User"
        }
        
        # Pequeña pausa para asegurar diferencia en timestamps
        import time
        time.sleep(0.1)
        
        update_response = client.put("/accounts/me", json=update_data, headers=headers)
        assert update_response.status_code == 200
        updated_data = update_response.json()
        
        # Verificar que se mantiene rastro de auditoría básico
        assert updated_data["created_at"] == initial_created_at  # No debe cambiar
        assert updated_data["updated_at"] is not None  # Debe actualizarse
        assert updated_data["updated_at"] != initial_updated_at  # Debe ser diferente
        
        # Verificar que los cambios se reflejan
        assert updated_data["first_name"] == "Updated"
        assert updated_data["last_name"] == "User"
        
        # Verificar que el timestamp de actualización es reciente
        # Simplemente verificar que updated_at no es None y es diferente del inicial
        assert updated_data["updated_at"] is not None
        assert updated_data["updated_at"] != initial_updated_at