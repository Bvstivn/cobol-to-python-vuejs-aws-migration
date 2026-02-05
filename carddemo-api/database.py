"""
Configuración de base de datos para CardDemo API
"""
from sqlmodel import SQLModel, create_engine, Session
from config import settings
from services.logging_service import get_secure_logger, get_db_error_handler
import time
from typing import Generator, Optional, Any, Callable
from contextlib import contextmanager
from functools import wraps

# Configurar logging seguro
logger = get_secure_logger("database")

# Crear engine de base de datos
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL queries en modo debug
    connect_args={"check_same_thread": False}  # Necesario para SQLite
)


def create_db_and_tables():
    """Crear base de datos y todas las tablas con manejo de errores"""
    error_handler = get_db_error_handler()
    
    while True:
        try:
            SQLModel.metadata.create_all(engine)
            logger.info("✅ Base de datos y tablas creadas exitosamente")
            error_handler.reset_retry_count()
            break
            
        except Exception as e:
            error_info = error_handler.handle_database_error(
                e, 
                "create_db_and_tables",
                operation_type="DDL"
            )
            
            if error_handler.should_retry(e):
                error_handler.increment_retry()
                retry_delay = error_handler.retry_delay * error_handler.retry_count
                logger.warning(f"Reintentando creación de BD en {retry_delay} segundos...")
                time.sleep(retry_delay)
                continue
            else:
                logger.critical("No se pudo crear la base de datos después de múltiples intentos")
                raise


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Obtener sesión de base de datos con manejo robusto de errores
    
    Yields:
        Session: Sesión de base de datos
        
    Raises:
        Exception: Si no se puede establecer conexión después de reintentos
    """
    error_handler = get_db_error_handler()
    session = None
    
    while True:
        try:
            session = Session(engine)
            
            # Verificar conectividad con una query simple
            from sqlmodel import text
            session.execute(text("SELECT 1"))
            
            logger.debug("Sesión de base de datos establecida exitosamente")
            error_handler.reset_retry_count()
            
            yield session
            break
            
        except Exception as e:
            if session:
                session.close()
            
            error_info = error_handler.handle_database_error(
                e,
                "get_db_session",
                operation_type="connection"
            )
            
            if error_handler.should_retry(e):
                error_handler.increment_retry()
                retry_delay = error_handler.retry_delay * error_handler.retry_count
                logger.warning(f"Reintentando conexión a BD en {retry_delay} segundos...")
                time.sleep(retry_delay)
                continue
            else:
                logger.critical("No se pudo establecer conexión a BD después de múltiples intentos")
                raise
        
        finally:
            if session:
                try:
                    session.close()
                    logger.debug("Sesión de base de datos cerrada")
                except Exception as e:
                    logger.error(f"Error cerrando sesión de BD: {e}")


def get_session():
    """Obtener sesión de base de datos para dependency injection (FastAPI)"""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


def execute_with_retry(operation: Callable, operation_name: str, **kwargs) -> Any:
    """
    Ejecutar operación de base de datos con reintentos automáticos
    
    Args:
        operation: Función a ejecutar
        operation_name: Nombre descriptivo de la operación
        **kwargs: Argumentos para la operación
        
    Returns:
        Resultado de la operación
        
    Raises:
        Exception: Si la operación falla después de todos los reintentos
    """
    error_handler = get_db_error_handler()
    
    while True:
        try:
            result = operation(**kwargs)
            error_handler.reset_retry_count()
            logger.debug(f"Operación {operation_name} ejecutada exitosamente")
            return result
            
        except Exception as e:
            error_info = error_handler.handle_database_error(
                e,
                operation_name,
                **kwargs
            )
            
            if error_handler.should_retry(e):
                error_handler.increment_retry()
                retry_delay = error_handler.retry_delay * error_handler.retry_count
                logger.warning(f"Reintentando {operation_name} en {retry_delay} segundos...")
                time.sleep(retry_delay)
                continue
            else:
                logger.error(f"Operación {operation_name} falló después de múltiples intentos")
                raise


def database_operation(operation_name: str):
    """
    Decorador para operaciones de base de datos con manejo automático de errores
    
    Args:
        operation_name: Nombre descriptivo de la operación
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return execute_with_retry(
                lambda: func(*args, **kwargs),
                operation_name
            )
        return wrapper
    return decorator


def check_database_health() -> dict:
    """
    Verificar salud de la base de datos
    
    Returns:
        Dict con información de salud de la BD
    """
    health_info = {
        'status': 'unknown',
        'connection': False,
        'tables_exist': False,
        'last_check': time.time(),
        'error': None
    }
    
    try:
        with get_db_session() as session:
            # Verificar conexión
            from sqlmodel import text
            session.execute(text("SELECT 1"))
            health_info['connection'] = True
            
            # Verificar que las tablas principales existen
            from models.database_models import User
            user_count = session.query(User).count()
            health_info['tables_exist'] = True
            health_info['user_count'] = user_count
            
            health_info['status'] = 'healthy'
            logger.debug("Verificación de salud de BD exitosa")
            
    except Exception as e:
        health_info['status'] = 'unhealthy'
        health_info['error'] = str(e)
        logger.error(f"Verificación de salud de BD falló: {e}")
    
    return health_info


@database_operation("init_database")
def init_database():
    """Inicializar base de datos con datos de prueba"""
    from models.database_models import User, Account, CreditCard, Transaction
    from services.auth_service import AuthService
    from datetime import datetime, date
    from decimal import Decimal
    
    create_db_and_tables()
    
    with get_db_session() as session:
        # Verificar si ya hay datos
        existing_user = session.query(User).first()
        if existing_user:
            logger.info("ℹ️  Base de datos ya tiene datos, saltando inicialización")
            return
        
        logger.info("📝 Inicializando base de datos con datos de prueba...")
        
        # Crear usuarios de prueba
        auth_service = AuthService()
        
        # Usuario administrador
        admin_user = User(
            username="ADMIN001",
            email="admin@carddemo.com",
            hashed_password=auth_service.hash_password("PASSWORD"),
            is_active=True
        )
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)
        
        # Usuario regular
        regular_user = User(
            username="USER0001",
            email="user@carddemo.com",
            hashed_password=auth_service.hash_password("PASSWORD"),
            is_active=True
        )
        session.add(regular_user)
        session.commit()
        session.refresh(regular_user)
        
        # Crear cuentas
        admin_account = Account(
            user_id=admin_user.id,
            account_number="1000000001",
            first_name="Admin",
            last_name="User",
            phone="555-0001",
            address="123 Admin St",
            city="Admin City",
            state="AC",
            zip_code="12345"
        )
        session.add(admin_account)
        
        user_account = Account(
            user_id=regular_user.id,
            account_number="1000000002",
            first_name="John",
            last_name="Doe",
            phone="555-0002",
            address="456 User Ave",
            city="User City",
            state="UC",
            zip_code="67890"
        )
        session.add(user_account)
        session.commit()
        session.refresh(admin_account)
        session.refresh(user_account)
        
        # Crear tarjetas de crédito
        admin_card = CreditCard(
            account_id=admin_account.id,
            card_number="4111111111111111",  # Número de prueba Visa
            card_type="VISA",
            expiry_month=12,
            expiry_year=2025,
            status="ACTIVE",
            credit_limit=Decimal("10000.00"),
            available_credit=Decimal("8500.00")
        )
        session.add(admin_card)
        
        user_card1 = CreditCard(
            account_id=user_account.id,
            card_number="5555555555554444",  # Número de prueba Mastercard
            card_type="MASTERCARD",
            expiry_month=6,
            expiry_year=2026,
            status="ACTIVE",
            credit_limit=Decimal("5000.00"),
            available_credit=Decimal("4200.00")
        )
        session.add(user_card1)
        
        user_card2 = CreditCard(
            account_id=user_account.id,
            card_number="378282246310005",  # Número de prueba Amex
            card_type="AMEX",
            expiry_month=3,
            expiry_year=2027,
            status="ACTIVE",
            credit_limit=Decimal("7500.00"),
            available_credit=Decimal("7500.00")
        )
        session.add(user_card2)
        session.commit()
        session.refresh(admin_card)
        session.refresh(user_card1)
        session.refresh(user_card2)
        
        # Crear transacciones de ejemplo
        transactions = [
            Transaction(
                card_id=admin_card.id,
                transaction_date=datetime(2024, 1, 15, 10, 30),
                merchant_name="Amazon",
                amount=Decimal("89.99"),
                transaction_type="PURCHASE",
                status="COMPLETED",
                description="Online purchase"
            ),
            Transaction(
                card_id=admin_card.id,
                transaction_date=datetime(2024, 1, 14, 15, 45),
                merchant_name="Starbucks",
                amount=Decimal("12.50"),
                transaction_type="PURCHASE",
                status="COMPLETED",
                description="Coffee purchase"
            ),
            Transaction(
                card_id=user_card1.id,
                transaction_date=datetime(2024, 1, 13, 9, 20),
                merchant_name="Gas Station",
                amount=Decimal("45.00"),
                transaction_type="PURCHASE",
                status="COMPLETED",
                description="Fuel purchase"
            ),
            Transaction(
                card_id=user_card1.id,
                transaction_date=datetime(2024, 1, 12, 18, 30),
                merchant_name="Restaurant",
                amount=Decimal("67.80"),
                transaction_type="PURCHASE",
                status="COMPLETED",
                description="Dinner"
            ),
            Transaction(
                card_id=user_card1.id,
                transaction_date=datetime(2024, 1, 10, 12, 0),
                merchant_name="Payment",
                amount=Decimal("200.00"),
                transaction_type="PAYMENT",
                status="COMPLETED",
                description="Credit card payment"
            )
        ]
        
        for transaction in transactions:
            session.add(transaction)
        
        session.commit()
        logger.info("✅ Datos de prueba inicializados exitosamente")
        logger.info("👤 Usuarios creados: ADMIN001/PASSWORD, USER0001/PASSWORD")