"""
Tests de integración para endpoints de autenticación
Feature: carddemo-api-migration
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel

from main import app
from database import get_session
from services.auth_service import AuthService
from models.database_models import User


@pytest.fixture
def test_engine():
    """Crear engine de prueba con SQLite en memoria"""
    engine = create_engine(
        "sqlite:///:memory:", 
        echo=False,
        connect_args={"check_same_thread": False}  # Permitir uso en múltiples threads
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Crear sesión de prueba"""
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def client(test_session):
    """Cliente de prueba con base de datos en memoria"""
    def get_test_session():
        return test_session
    
    app.dependency_overrides[get_session] = get_test_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(test_session):
    """Crear usuario de prueba en la base de datos"""
    auth_service = AuthService()
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=auth_service.hash_password("testpassword"),
        is_active=True
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user


@pytest.fixture
def inactive_user(test_session):
    """Crear usuario inactivo de prueba"""
    auth_service = AuthService()
    user = User(
        username="inactive",
        email="inactive@example.com",
        hashed_password=auth_service.hash_password("password"),
        is_active=False
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user


class TestLoginEndpoint:
    """Tests para el endpoint POST /auth/login"""
    
    def test_successful_login(self, client, test_user):
        """Test de login exitoso con credenciales válidas"""
        response = client.post(
            "/auth/login",
            json={
                "username": "testuser",
                "password": "testpassword"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura de respuesta
        assert "access_token" in data
        assert "token_type" in data
        assert "user" in data
        
        # Verificar token
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
        
        # Verificar información del usuario
        user_data = data["user"]
        assert user_data["username"] == "testuser"
        assert user_data["email"] == "test@example.com"
        assert user_data["is_active"] is True
        assert "id" in user_data
    
    def test_invalid_username(self, client, test_user):
        """Test de login con username inválido"""
        response = client.post(
            "/auth/login",
            json={
                "username": "nonexistent",
                "password": "testpassword"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Credenciales inválidas"
    
    def test_invalid_password(self, client, test_user):
        """Test de login con contraseña inválida"""
        response = client.post(
            "/auth/login",
            json={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Credenciales inválidas"
    
    def test_inactive_user_login(self, client, inactive_user):
        """Test de login con usuario inactivo"""
        response = client.post(
            "/auth/login",
            json={
                "username": "inactive",
                "password": "password"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Credenciales inválidas"
    
    def test_missing_username(self, client):
        """Test de login sin username"""
        response = client.post(
            "/auth/login",
            json={
                "password": "testpassword"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_missing_password(self, client):
        """Test de login sin password"""
        response = client.post(
            "/auth/login",
            json={
                "username": "testuser"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_empty_credentials(self, client):
        """Test de login con credenciales vacías"""
        response = client.post(
            "/auth/login",
            json={
                "username": "",
                "password": ""
            }
        )
        
        assert response.status_code == 422  # Validation error por longitud mínima


class TestLogoutEndpoint:
    """Tests para el endpoint POST /auth/logout"""
    
    def test_successful_logout(self, client, test_user):
        """Test de logout exitoso con token válido"""
        # Primero hacer login para obtener token
        login_response = client.post(
            "/auth/login",
            json={
                "username": "testuser",
                "password": "testpassword"
            }
        )
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Hacer logout con el token
        logout_response = client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert logout_response.status_code == 200
        data = logout_response.json()
        assert "message" in data
        assert "testuser" in data["message"]
        assert "cerrado sesión exitosamente" in data["message"]
        assert "detail" in data
    
    def test_logout_without_token(self, client):
        """Test de logout sin token de autorización"""
        response = client.post("/auth/logout")
        
        assert response.status_code == 401  # Unauthorized - no token provided
    
    def test_logout_with_invalid_token(self, client):
        """Test de logout con token inválido"""
        response = client.post(
            "/auth/logout",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Token inválido o expirado"


class TestGetCurrentUserEndpoint:
    """Tests para el endpoint GET /auth/me"""
    
    def test_get_current_user_info(self, client, test_user):
        """Test de obtener información del usuario actual"""
        # Primero hacer login para obtener token
        login_response = client.post(
            "/auth/login",
            json={
                "username": "testuser",
                "password": "testpassword"
            }
        )
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Obtener información del usuario
        me_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert me_response.status_code == 200
        data = me_response.json()
        
        # Verificar información del usuario
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["is_active"] is True
        assert "id" in data
    
    def test_get_current_user_without_token(self, client):
        """Test de obtener usuario actual sin token"""
        response = client.get("/auth/me")
        
        assert response.status_code == 401  # Unauthorized - no token provided
    
    def test_get_current_user_with_invalid_token(self, client):
        """Test de obtener usuario actual con token inválido"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Token inválido o expirado"


class TestAuthenticationFlow:
    """Tests de flujo completo de autenticación"""
    
    def test_complete_auth_flow(self, client, test_user):
        """Test de flujo completo: login → obtener info → logout"""
        # 1. Login
        login_response = client.post(
            "/auth/login",
            json={
                "username": "testuser",
                "password": "testpassword"
            }
        )
        
        assert login_response.status_code == 200
        login_data = login_response.json()
        token = login_data["access_token"]
        
        # 2. Obtener información del usuario
        me_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["username"] == login_data["user"]["username"]
        
        # 3. Logout
        logout_response = client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert logout_response.status_code == 200
        logout_data = logout_response.json()
        assert "testuser" in logout_data["message"]
    
    def test_token_reuse_after_logout(self, client, test_user):
        """Test de que el token sigue siendo válido después del logout (JWT stateless)"""
        # Login
        login_response = client.post(
            "/auth/login",
            json={
                "username": "testuser",
                "password": "testpassword"
            }
        )
        
        token = login_response.json()["access_token"]
        
        # Logout
        logout_response = client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert logout_response.status_code == 200
        
        # El token debería seguir siendo válido (JWT stateless)
        # En una implementación real, se podría usar una blacklist de tokens
        me_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert me_response.status_code == 200
        # Nota: En JWT stateless, el token sigue siendo válido hasta que expire
        # Para invalidar tokens inmediatamente, se necesitaría una blacklist