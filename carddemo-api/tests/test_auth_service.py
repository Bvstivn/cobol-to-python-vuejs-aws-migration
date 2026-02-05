"""
Tests para el servicio de autenticación
Feature: carddemo-api-migration
"""
import pytest
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, create_engine, SQLModel
from jose import jwt

from services.auth_service import AuthService
from models.database_models import User


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


@pytest.fixture
def auth_service():
    """Crear servicio de autenticación"""
    return AuthService()


@pytest.fixture
def test_user(test_session, auth_service):
    """Crear usuario de prueba"""
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


# Feature: carddemo-api-migration, Property 1: Autenticación con credenciales válidas genera tokens JWT
def test_valid_credentials_generate_jwt_tokens(test_session, auth_service, test_user):
    """
    Propiedad 1: Autenticación con credenciales válidas genera tokens JWT
    Valida: Requisitos 1.1
    
    Para cualquier usuario con credenciales válidas, cuando se autentica,
    el sistema debe generar un token JWT válido
    """
    # Autenticar con credenciales válidas
    authenticated_user = auth_service.authenticate_user(
        test_session, "testuser", "testpassword"
    )
    
    # Debe devolver el usuario
    assert authenticated_user is not None
    assert authenticated_user.username == "testuser"
    assert authenticated_user.email == "test@example.com"
    
    # Crear token JWT
    token_data = auth_service.create_user_token_data(authenticated_user)
    token = auth_service.create_access_token(token_data)
    
    # El token debe ser una string no vacía
    assert isinstance(token, str)
    assert len(token) > 0
    
    # El token debe ser decodificable
    payload = auth_service.verify_token(token)
    assert payload is not None
    assert payload["sub"] == str(authenticated_user.id)
    assert payload["username"] == "testuser"
    assert payload["email"] == "test@example.com"


# Feature: carddemo-api-migration, Property 2: Credenciales inválidas son rechazadas consistentemente
def test_invalid_credentials_rejected_consistently(test_session, auth_service, test_user):
    """
    Propiedad 2: Credenciales inválidas son rechazadas consistentemente
    Valida: Requisitos 1.2
    
    Para cualquier conjunto de credenciales inválidas, el sistema debe
    devolver error de autenticación y denegar el acceso
    """
    # Usuario inexistente
    result = auth_service.authenticate_user(test_session, "nonexistent", "password")
    assert result is None
    
    # Contraseña incorrecta
    result = auth_service.authenticate_user(test_session, "testuser", "wrongpassword")
    assert result is None
    
    # Username vacío
    result = auth_service.authenticate_user(test_session, "", "testpassword")
    assert result is None
    
    # Contraseña vacía
    result = auth_service.authenticate_user(test_session, "testuser", "")
    assert result is None
    
    # Ambos vacíos
    result = auth_service.authenticate_user(test_session, "", "")
    assert result is None


# Feature: carddemo-api-migration, Property 3: Validación de tokens JWT en endpoints protegidos
def test_jwt_token_validation_in_protected_endpoints(test_session, auth_service, test_user):
    """
    Propiedad 3: Validación de tokens JWT en endpoints protegidos
    Valida: Requisitos 1.3
    
    Para cualquier token JWT válido, el sistema debe validar el token
    y permitir acceso a endpoints protegidos
    """
    # Crear token válido
    token_data = auth_service.create_user_token_data(test_user)
    valid_token = auth_service.create_access_token(token_data)
    
    # El token debe ser válido
    payload = auth_service.verify_token(valid_token)
    assert payload is not None
    assert payload["sub"] == str(test_user.id)
    
    # Debe poder obtener el usuario desde el token
    current_user = auth_service.get_current_user(test_session, valid_token)
    assert current_user is not None
    assert current_user.id == test_user.id
    assert current_user.username == test_user.username


# Feature: carddemo-api-migration, Property 4: Tokens expirados o inválidos son rechazados
def test_expired_invalid_tokens_rejected(test_session, auth_service, test_user):
    """
    Propiedad 4: Tokens expirados o inválidos son rechazados
    Valida: Requisitos 1.4
    
    Para cualquier token JWT expirado o inválido, el sistema debe
    devolver error de autorización y denegar el acceso
    """
    # Token expirado
    token_data = auth_service.create_user_token_data(test_user)
    expired_token = auth_service.create_access_token(
        token_data, 
        expires_delta=timedelta(seconds=-1)  # Expirado hace 1 segundo
    )
    
    payload = auth_service.verify_token(expired_token)
    assert payload is None
    
    current_user = auth_service.get_current_user(test_session, expired_token)
    assert current_user is None
    
    # Token malformado
    invalid_token = "invalid.token.here"
    payload = auth_service.verify_token(invalid_token)
    assert payload is None
    
    current_user = auth_service.get_current_user(test_session, invalid_token)
    assert current_user is None
    
    # Token vacío
    payload = auth_service.verify_token("")
    assert payload is None
    
    current_user = auth_service.get_current_user(test_session, "")
    assert current_user is None
    
    # Token con firma incorrecta
    fake_token = jwt.encode(
        {"sub": str(test_user.id), "username": "testuser"}, 
        "wrong-secret", 
        algorithm="HS256"
    )
    payload = auth_service.verify_token(fake_token)
    assert payload is None


# Feature: carddemo-api-migration, Property 5: Almacenamiento seguro de contraseñas
def test_secure_password_storage(auth_service):
    """
    Propiedad 5: Almacenamiento seguro de contraseñas
    Valida: Requisitos 1.5
    
    Para cualquier contraseña de usuario, el sistema debe almacenarla
    hasheada usando métodos seguros estándar, nunca en texto plano
    """
    password = "mysecretpassword"
    
    # Hashear contraseña
    hashed = auth_service.hash_password(password)
    
    # El hash debe ser diferente de la contraseña original
    assert hashed != password
    
    # El hash debe tener longitud apropiada para bcrypt
    assert len(hashed) >= 60  # bcrypt hashes son típicamente 60 caracteres
    
    # El hash debe comenzar con $2b$ (bcrypt identifier)
    assert hashed.startswith("$2b$")
    
    # Debe poder verificar la contraseña original
    assert auth_service.verify_password(password, hashed)
    
    # No debe verificar contraseñas incorrectas
    assert not auth_service.verify_password("wrongpassword", hashed)
    
    # Hashear la misma contraseña múltiples veces debe dar hashes diferentes
    hash1 = auth_service.hash_password(password)
    hash2 = auth_service.hash_password(password)
    assert hash1 != hash2
    
    # Pero ambos deben verificar correctamente
    assert auth_service.verify_password(password, hash1)
    assert auth_service.verify_password(password, hash2)


def test_user_token_data_creation(auth_service, test_user):
    """Test de creación de datos para token JWT"""
    token_data = auth_service.create_user_token_data(test_user)
    
    assert token_data["sub"] == str(test_user.id)
    assert token_data["username"] == test_user.username
    assert token_data["email"] == test_user.email
    assert token_data["is_active"] == test_user.is_active


def test_inactive_user_authentication(test_session, auth_service):
    """Test de autenticación con usuario inactivo"""
    # Crear usuario inactivo
    inactive_user = User(
        username="inactive",
        email="inactive@example.com",
        hashed_password=auth_service.hash_password("password"),
        is_active=False
    )
    test_session.add(inactive_user)
    test_session.commit()
    
    # No debe poder autenticarse
    result = auth_service.authenticate_user(test_session, "inactive", "password")
    assert result is None


def test_token_with_custom_expiration(auth_service, test_user):
    """Test de token con tiempo de expiración personalizado"""
    token_data = auth_service.create_user_token_data(test_user)
    
    # Token con expiración de 1 hora
    custom_expiry = timedelta(hours=1)
    token = auth_service.create_access_token(token_data, expires_delta=custom_expiry)
    
    # Verificar que el token es válido
    payload = auth_service.verify_token(token)
    assert payload is not None
    
    # Verificar tiempo de expiración
    exp = payload["exp"]
    if isinstance(exp, (int, float)):
        exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
    else:
        exp_datetime = exp.replace(tzinfo=timezone.utc) if exp.tzinfo is None else exp
    
    now = datetime.now(timezone.utc)
    
    # Debe expirar en aproximadamente 1 hora
    time_diff = exp_datetime - now
    assert 3500 <= time_diff.total_seconds() <= 3700  # ~1 hora con margen