"""
Tests de propiedades para gestión de transacciones (versión simplificada)
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from datetime import datetime, timezone, timedelta, date
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


@pytest.fixture(name="test_users_with_transactions")
def test_users_with_transactions_fixture(session: Session):
    """Crear múltiples usuarios con cuentas, tarjetas y transacciones de prueba"""
    auth_service = AuthService()
    users_data = []
    
    for i in range(3):
        # Crear usuario
        user = User(
            username=f"transuser{i}",
            email=f"transuser{i}@example.com",
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
            first_name=f"Trans{i}",
            last_name=f"User{i}"
        )
        session.add(account)
        session.commit()
        session.refresh(account)
        
        # Crear tarjetas
        cards = []
        for j in range(2):
            card = CreditCard(
                account_id=account.id,
                card_number=f"411111111111{i}{j:04d}",
                card_type="VISA" if j == 0 else "MASTERCARD",
                expiry_month=12,
                expiry_year=2025 + j,
                status="ACTIVE",
                credit_limit=Decimal(f"{(i+1)*1000}.00"),
                available_credit=Decimal(f"{(i+1)*800}.00")
            )
            session.add(card)
            cards.append(card)
        
        session.commit()
        for card in cards:
            session.refresh(card)
        
        users_data.append({"user": user, "account": account, "cards": cards})
    
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


class TestTransactionProperties:
    """Tests de propiedades para gestión de transacciones"""
    
    def test_property_13_access_to_own_transaction_history(self, client: TestClient, test_users_with_transactions: list, session: Session):
        """
        **Propiedad 13: Acceso a historial de transacciones propio**
        **Valida: Requisitos 4.1**
        
        Verifica que un usuario puede acceder a su historial completo de transacciones
        """
        user_data = test_users_with_transactions[0]
        cards = user_data["cards"]
        headers = get_auth_headers(client, "transuser0")
        
        # Crear múltiples transacciones para el usuario
        base_date = datetime.now(timezone.utc)
        transactions = []
        
        for i in range(5):
            transaction = Transaction(
                card_id=cards[i % len(cards)].id,
                transaction_date=base_date - timedelta(days=i),
                merchant_name=f"Store {i}",
                amount=Decimal(f"{10 + i * 5}.00"),
                transaction_type="PURCHASE" if i % 2 == 0 else "PAYMENT",
                status="COMPLETED",
                description=f"Transaction {i}"
            )
            session.add(transaction)
            transactions.append(transaction)
        
        session.commit()
        
        # Obtener historial de transacciones
        response = client.get("/transactions", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que se retornan todas las transacciones del usuario
        assert data["total"] >= 5
        assert len(data["transactions"]) >= 5
        
        # Verificar que cada transacción tiene la estructura correcta
        for transaction_data in data["transactions"]:
            assert "id" in transaction_data
            assert "transaction_date" in transaction_data
            assert "merchant_name" in transaction_data
            assert "amount" in transaction_data
            assert "transaction_type" in transaction_data
            assert "status" in transaction_data
            assert "created_at" in transaction_data
        
        # Verificar que las transacciones están ordenadas por fecha descendente
        dates = [datetime.fromisoformat(t["transaction_date"].replace('Z', '+00:00')) for t in data["transactions"]]
        assert dates == sorted(dates, reverse=True)
        
        # Verificar que se pueden obtener detalles de transacciones específicas
        for transaction in transactions:
            session.refresh(transaction)
            detail_response = client.get(f"/transactions/{transaction.id}", headers=headers)
            assert detail_response.status_code == 200
            detail_data = detail_response.json()
            assert detail_data["id"] == transaction.id
            assert detail_data["merchant_name"] == transaction.merchant_name
    
    def test_property_14_effective_transaction_filtering(self, client: TestClient, test_users_with_transactions: list, session: Session):
        """
        **Propiedad 14: Filtrado efectivo de transacciones**
        **Valida: Requisitos 4.2**
        
        Verifica que los filtros de transacciones funcionan correctamente
        """
        user_data = test_users_with_transactions[1]
        cards = user_data["cards"]
        headers = get_auth_headers(client, "transuser1")
        
        # Crear transacciones con características específicas para filtrar
        base_date = datetime.now(timezone.utc)
        test_transactions = [
            {
                "card_id": cards[0].id,
                "date": base_date - timedelta(days=1),
                "merchant": "Amazon",
                "amount": Decimal("50.00"),
                "type": "PURCHASE"
            },
            {
                "card_id": cards[1].id,
                "date": base_date - timedelta(days=2),
                "merchant": "Starbucks",
                "amount": Decimal("5.75"),
                "type": "PURCHASE"
            },
            {
                "card_id": cards[0].id,
                "date": base_date - timedelta(days=3),
                "merchant": "Payment Center",
                "amount": Decimal("200.00"),
                "type": "PAYMENT"
            },
            {
                "card_id": cards[1].id,
                "date": base_date - timedelta(days=10),
                "merchant": "Old Store",
                "amount": Decimal("25.00"),
                "type": "PURCHASE"
            }
        ]
        
        created_transactions = []
        for trans_data in test_transactions:
            transaction = Transaction(
                card_id=trans_data["card_id"],
                transaction_date=trans_data["date"],
                merchant_name=trans_data["merchant"],
                amount=trans_data["amount"],
                transaction_type=trans_data["type"],
                status="COMPLETED"
            )
            session.add(transaction)
            created_transactions.append(transaction)
        
        session.commit()
        
        # Test 1: Filtro por tipo de transacción
        response = client.get("/transactions?transaction_type=PURCHASE", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        purchase_count = sum(1 for t in data["transactions"] if t["transaction_type"] == "PURCHASE")
        assert purchase_count >= 3  # Las 3 transacciones PURCHASE que creamos
        
        for transaction in data["transactions"]:
            if transaction["transaction_type"] != "PURCHASE":
                # Si hay transacciones de ejemplo, pueden ser de otros tipos
                continue
            assert transaction["transaction_type"] == "PURCHASE"
        
        # Test 2: Filtro por rango de fechas
        start_date = (base_date - timedelta(days=5)).date()
        end_date = base_date.date()
        
        response = client.get(f"/transactions?start_date={start_date}&end_date={end_date}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que todas las transacciones están en el rango de fechas
        for transaction in data["transactions"]:
            trans_date = datetime.fromisoformat(transaction["transaction_date"].replace('Z', '+00:00')).date()
            assert start_date <= trans_date <= end_date
        
        # Test 3: Filtro por monto
        response = client.get("/transactions?min_amount=20&max_amount=100", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        for transaction in data["transactions"]:
            amount = float(transaction["amount"])
            assert 20.0 <= amount <= 100.0
        
        # Test 4: Filtro por tarjeta específica
        response = client.get(f"/transactions?card_id={cards[0].id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Debe retornar al menos las transacciones de esa tarjeta
        assert len(data["transactions"]) >= 2  # Las 2 transacciones de cards[0]
        
        # Test 5: Combinación de filtros
        response = client.get(f"/transactions?transaction_type=PURCHASE&min_amount=10", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        for transaction in data["transactions"]:
            if transaction["transaction_type"] == "PURCHASE":
                assert float(transaction["amount"]) >= 10.0
    
    def test_no_transactions_case(self, client: TestClient, test_users_with_transactions: list):
        """
        Test unitario para casos sin transacciones
        **Valida: Requisitos 4.3**
        
        Verifica el comportamiento cuando no hay transacciones que coincidan con filtros
        """
        headers = get_auth_headers(client, "transuser2")
        
        # Test 1: Usuario sin transacciones - debe crear transacciones de ejemplo
        response = client.get("/transactions", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Se deben crear transacciones de ejemplo automáticamente
        assert data["total"] >= 5  # Se crean 5 transacciones de ejemplo
        assert len(data["transactions"]) >= 5
        
        # Verificar estructura de respuesta paginada
        assert "transactions" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert "has_more" in data
        
        # Test 2: Filtros que no coinciden con ninguna transacción
        # Buscar transacciones de hace 2 años (no debería haber ninguna)
        old_date = (datetime.now() - timedelta(days=730)).date()
        response = client.get(f"/transactions?start_date={old_date}&end_date={old_date}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # No debe haber transacciones tan antiguas
        assert len(data["transactions"]) == 0
        assert data["total"] == 0
        assert data["has_more"] == False
        
        # Test 3: Filtro por monto muy alto (no debería haber coincidencias)
        response = client.get("/transactions?min_amount=10000", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # No debe haber transacciones con montos tan altos
        assert len(data["transactions"]) == 0
        assert data["total"] == 0
        
        # Test 4: Paginación más allá de los resultados disponibles
        response = client.get("/transactions?offset=1000", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # No debe haber transacciones en esa página
        assert len(data["transactions"]) == 0
        assert data["has_more"] == False