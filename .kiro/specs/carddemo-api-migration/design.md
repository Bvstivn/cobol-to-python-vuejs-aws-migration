# Documento de Diseño: Migración API CardDemo

## Resumen

Este documento describe el diseño técnico para migrar la aplicación mainframe CardDemo COBOL a una API REST moderna en Python. El diseño se enfoca en crear un producto mínimo viable (MVP) que replique la funcionalidad central usando FastAPI, SQLite, y autenticación JWT, proporcionando una base sólida para expansión futura.

## Arquitectura

### Arquitectura General

La aplicación seguirá una arquitectura de capas limpia con separación clara de responsabilidades:

```
┌─────────────────────────────────────────┐
│              API Layer                  │
│         (FastAPI Routes)                │
├─────────────────────────────────────────┤
│            Service Layer                │
│    (Business Logic & Validation)        │
├─────────────────────────────────────────┤
│           Repository Layer              │
│        (Data Access Logic)              │
├─────────────────────────────────────────┤
│            Data Layer                   │
│         (SQLite Database)               │
└─────────────────────────────────────────┘
```

### Patrones Arquitectónicos

- **Inyección de Dependencias**: Uso de FastAPI Depends para gestión de dependencias
- **Repository Pattern**: Abstracción de acceso a datos para facilitar testing y mantenimiento
- **Service Layer**: Lógica de negocio centralizada y reutilizable
- **DTO Pattern**: Modelos Pydantic para validación y serialización de datos

### Stack Tecnológico

- **Framework Web**: FastAPI 0.104+
- **Base de Datos**: SQLite 3.x
- **ORM**: SQLAlchemy 2.x con SQLModel
- **Validación**: Pydantic 2.x
- **Autenticación**: JWT con python-jose
- **Hashing**: bcrypt para contraseñas
- **Testing**: pytest con pytest-asyncio
- **Documentación**: Automática con OpenAPI/Swagger

## Componentes e Interfaces

### 1. Servicio de Autenticación

**Responsabilidades:**
- Validación de credenciales de usuario
- Generación y validación de tokens JWT
- Gestión de sesiones y expiración de tokens

**Interfaces Principales:**
```python
class AuthService:
    async def authenticate_user(username: str, password: str) -> Optional[User]
    async def create_access_token(user_data: dict) -> str
    async def verify_token(token: str) -> Optional[dict]
    async def hash_password(password: str) -> str
    async def verify_password(plain_password: str, hashed_password: str) -> bool
```

**Endpoints:**
- `POST /auth/login` - Autenticación de usuario
- `POST /auth/logout` - Cierre de sesión (invalidación de token)

### 2. Gestor de Cuentas

**Responsabilidades:**
- Gestión de información de cuentas de usuario
- Validación de datos de cuenta
- Auditoría de cambios

**Interfaces Principales:**
```python
class AccountService:
    async def get_account_by_user_id(user_id: int) -> Optional[Account]
    async def update_account(user_id: int, account_data: AccountUpdate) -> Account
    async def validate_account_data(account_data: AccountUpdate) -> bool
```

**Endpoints:**
- `GET /accounts/me` - Obtener información de cuenta del usuario autenticado
- `PUT /accounts/me` - Actualizar información de cuenta

### 3. Servicio de Tarjetas

**Responsabilidades:**
- Gestión de tarjetas de crédito asociadas a cuentas
- Enmascaramiento de información sensible
- Validación de permisos de acceso

**Interfaces Principales:**
```python
class CardService:
    async def get_cards_by_user_id(user_id: int) -> List[Card]
    async def mask_card_number(card_number: str) -> str
    async def get_card_by_id(card_id: int, user_id: int) -> Optional[Card]
```

**Endpoints:**
- `GET /cards` - Listar tarjetas del usuario autenticado
- `GET /cards/{card_id}` - Obtener detalles de tarjeta específica

### 4. Servicio de Transacciones

**Responsabilidades:**
- Consulta de historial de transacciones
- Filtrado y paginación de resultados
- Validación de permisos de acceso a transacciones

**Interfaces Principales:**
```python
class TransactionService:
    async def get_transactions_by_user_id(
        user_id: int, 
        filters: TransactionFilters
    ) -> List[Transaction]
    async def get_transaction_by_id(
        transaction_id: int, 
        user_id: int
    ) -> Optional[Transaction]
```

**Endpoints:**
- `GET /transactions` - Listar transacciones con filtros opcionales
- `GET /transactions/{transaction_id}` - Obtener detalles de transacción específica

### 5. Monitor de Salud

**Responsabilidades:**
- Verificación de estado del sistema
- Monitoreo de conectividad de base de datos
- Reporte de métricas básicas del sistema

**Interfaces Principales:**
```python
class HealthService:
    async def check_system_health() -> HealthStatus
    async def check_database_connectivity() -> bool
    async def get_system_metrics() -> SystemMetrics
```

**Endpoints:**
- `GET /health` - Estado básico del sistema
- `GET /health/detailed` - Estado detallado con métricas

## Modelos de Datos

### Modelos de Base de Datos (SQLModel)

```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class Account(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    account_number: str = Field(unique=True, index=True)
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class CreditCard(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id")
    card_number: str = Field(index=True)  # Será encriptado
    card_type: str  # VISA, MASTERCARD, etc.
    expiry_month: int
    expiry_year: int
    status: str = Field(default="ACTIVE")  # ACTIVE, BLOCKED, EXPIRED
    credit_limit: Decimal
    available_credit: Decimal
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    card_id: int = Field(foreign_key="creditcard.id")
    transaction_date: datetime
    merchant_name: str
    amount: Decimal
    transaction_type: str  # PURCHASE, PAYMENT, REFUND
    status: str = Field(default="COMPLETED")  # PENDING, COMPLETED, FAILED
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Modelos de API (Pydantic)

```python
class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class AccountResponse(BaseModel):
    id: int
    account_number: str
    first_name: str
    last_name: str
    phone: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]

class AccountUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None

class CardResponse(BaseModel):
    id: int
    masked_card_number: str  # **** **** **** 1234
    card_type: str
    expiry_month: int
    expiry_year: int
    status: str
    available_credit: Decimal

class TransactionResponse(BaseModel):
    id: int
    transaction_date: datetime
    merchant_name: str
    amount: Decimal
    transaction_type: str
    status: str
    description: Optional[str]

class TransactionFilters(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    card_id: Optional[int] = None
    transaction_type: Optional[str] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    limit: int = Field(default=50, le=100)
    offset: int = Field(default=0, ge=0)
```

## Propiedades de Corrección

*Una propiedad es una característica o comportamiento que debe mantenerse verdadero a través de todas las ejecuciones válidas de un sistema - esencialmente, una declaración formal sobre lo que el sistema debe hacer. Las propiedades sirven como el puente entre especificaciones legibles por humanos y garantías de corrección verificables por máquina.*

### Propiedad 1: Autenticación con credenciales válidas genera tokens JWT
*Para cualquier* usuario con credenciales válidas, cuando se autentica a través del endpoint de login, el sistema debe generar un token JWT válido que contenga la información correcta del usuario
**Valida: Requisitos 1.1**

### Propiedad 2: Credenciales inválidas son rechazadas consistentemente
*Para cualquier* conjunto de credenciales inválidas (usuario inexistente, contraseña incorrecta, formato inválido), el sistema debe devolver un error de autenticación y denegar el acceso
**Valida: Requisitos 1.2**

### Propiedad 3: Validación de tokens JWT en endpoints protegidos
*Para cualquier* endpoint protegido y cualquier token JWT, el sistema debe validar el token antes de procesar la petición, permitiendo acceso solo con tokens válidos
**Valida: Requisitos 1.3**

### Propiedad 4: Tokens expirados o inválidos son rechazados
*Para cualquier* token JWT expirado o inválido, el sistema debe devolver un error de autorización y denegar el acceso
**Valida: Requisitos 1.4**

### Propiedad 5: Almacenamiento seguro de contraseñas
*Para cualquier* contraseña de usuario, el sistema debe almacenarla hasheada usando métodos seguros estándar, nunca en texto plano, y el hash debe ser verificable
**Valida: Requisitos 1.5**

### Propiedad 6: Acceso a información de cuenta propia
*Para cualquier* usuario autenticado que solicite información de cuenta, el sistema debe devolver únicamente sus propios detalles completos de cuenta
**Valida: Requisitos 2.1**

### Propiedad 7: Persistencia de actualizaciones de cuenta válidas
*Para cualquier* actualización de cuenta con datos válidos, el sistema debe validar los datos, persistir los cambios, y reflejar las actualizaciones en consultas posteriores
**Valida: Requisitos 2.2**

### Propiedad 8: Aislamiento de datos entre usuarios
*Para cualquier* usuario autenticado, el sistema debe asegurar que solo puede acceder a sus propios datos (cuenta, tarjetas, transacciones) y nunca a datos de otros usuarios
**Valida: Requisitos 2.4, 3.5, 4.5**

### Propiedad 9: Auditoría de cambios de cuenta
*Para cualquier* actualización realizada en una cuenta, el sistema debe generar un registro de auditoría que capture qué cambió, cuándo y por quién
**Valida: Requisitos 2.5**

### Propiedad 10: Listado completo de tarjetas de usuario
*Para cualquier* usuario autenticado con tarjetas asociadas, el sistema debe devolver todas sus tarjetas cuando las solicite
**Valida: Requisitos 3.1**

### Propiedad 11: Enmascaramiento de números de tarjeta
*Para cualquier* tarjeta de crédito devuelta en respuestas de API, el número de tarjeta debe estar enmascarado mostrando solo los últimos 4 dígitos
**Valida: Requisitos 3.2**

### Propiedad 12: Completitud de respuestas de API
*Para cualquier* respuesta de API (tarjetas, transacciones, cuentas), debe incluir todos los campos requeridos según el esquema definido
**Valida: Requisitos 3.4, 4.4**

### Propiedad 13: Acceso a historial de transacciones propio
*Para cualquier* usuario autenticado que solicite transacciones, el sistema debe devolver su historial de transacciones completo
**Valida: Requisitos 4.1**

### Propiedad 14: Filtrado efectivo de transacciones
*Para cualquier* conjunto de filtros de transacciones (fecha, tarjeta, tipo, monto), el sistema debe devolver solo transacciones que cumplan todos los criterios especificados
**Valida: Requisitos 4.2**

### Propiedad 15: Manejo de errores de componentes del sistema
*Para cualquier* componente del sistema que no esté disponible, el monitor de salud debe detectar la falla y reportar el estado de error apropiado
**Valida: Requisitos 5.3**

### Propiedad 16: Verificación completa de salud del sistema
*Para cualquier* verificación de salud, el sistema debe incluir conectividad de base de datos y disponibilidad de servicios centrales en la evaluación
**Valida: Requisitos 5.4**

### Propiedad 17: Acceso sin autenticación a endpoint de salud
*Para cualquier* petición al endpoint básico de salud, el sistema debe responder sin requerir autenticación
**Valida: Requisitos 5.5**

### Propiedad 18: Transacciones ACID en base de datos
*Para cualquier* operación de escritura a la base de datos, el sistema debe asegurar cumplimiento ACID (atomicidad, consistencia, aislamiento, durabilidad)
**Valida: Requisitos 6.2**

### Propiedad 19: Manejo elegante de errores de base de datos
*Para cualquier* error de conexión o operación de base de datos, el sistema debe manejar el error elegantemente, devolver respuestas apropiadas y mantener estabilidad
**Valida: Requisitos 6.3**

### Propiedad 20: Formato JSON consistente
*Para cualquier* petición y respuesta de API, el sistema debe usar formato JSON válido y bien formado
**Valida: Requisitos 7.1**

### Propiedad 21: Validación de esquemas de entrada
*Para cualquier* petición con datos de entrada, el sistema debe validar los datos contra esquemas definidos antes de procesarlos
**Valida: Requisitos 7.2**

### Propiedad 22: Manejo consistente de errores de validación
*Para cualquier* fallo de validación de datos, el sistema debe devolver mensajes de error detallados con información específica de campo en formato consistente
**Valida: Requisitos 2.3, 7.3**

### Propiedad 23: Códigos de estado HTTP apropiados
*Para cualquier* respuesta de API, el sistema debe devolver el código de estado HTTP apropiado que corresponda al resultado de la operación
**Valida: Requisitos 7.4**

### Propiedad 24: IDs de correlación en respuestas
*Para cualquier* respuesta de API, el sistema debe incluir un ID de correlación único para rastreo y depuración
**Valida: Requisitos 7.5**

### Propiedad 25: Encriptación de datos sensibles
*Para cualquier* dato sensible (números de tarjeta, información personal), el sistema debe almacenarlo encriptado en la base de datos, nunca en texto plano
**Valida: Requisitos 8.1**

### Propiedad 26: Rate limiting para prevención de abuso
*Para cualquier* endpoint de API, el sistema debe aplicar limitación de tasa para prevenir abuso, bloqueando peticiones excesivas del mismo origen
**Valida: Requisitos 8.3**

### Propiedad 27: Logging seguro y completo
*Para cualquier* evento del sistema que se registre, el log debe incluir información necesaria para auditoría pero nunca datos sensibles como contraseñas o números de tarjeta completos
**Valida: Requisitos 6.4, 8.4**

### Propiedad 28: Sanitización de entrada para prevenir inyección
*Para cualquier* dato de entrada del usuario, el sistema debe validar y sanitizar la entrada para prevenir ataques de inyección (SQL, XSS, etc.)
**Valida: Requisitos 8.5**

## Manejo de Errores

### Estrategia de Manejo de Errores

La aplicación implementará un manejo de errores consistente y robusto:

**Categorías de Errores:**
1. **Errores de Validación (400)**: Datos de entrada inválidos o malformados
2. **Errores de Autenticación (401)**: Credenciales inválidas o tokens expirados
3. **Errores de Autorización (403)**: Acceso denegado a recursos
4. **Errores de Recurso No Encontrado (404)**: Entidades solicitadas no existen
5. **Errores de Servidor (500)**: Fallos internos del sistema o base de datos

**Formato Estándar de Error:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Los datos proporcionados no son válidos",
    "details": [
      {
        "field": "email",
        "message": "El formato del email no es válido"
      }
    ],
    "correlation_id": "req_123456789",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

**Manejo de Errores de Base de Datos:**
- Conexiones perdidas: Reintento automático con backoff exponencial
- Violaciones de integridad: Conversión a errores de validación apropiados
- Timeouts: Respuestas de error con código 503 (Service Unavailable)

**Logging de Errores:**
- Todos los errores se registran con nivel apropiado (ERROR, WARN, INFO)
- Información sensible se excluye de los logs
- Correlation IDs permiten rastreo de errores específicos

## Estrategia de Testing

### Enfoque Dual de Testing

La aplicación utilizará un enfoque dual que combina testing unitario y testing basado en propiedades:

**Testing Unitario:**
- Casos específicos y ejemplos concretos
- Casos límite y condiciones de error
- Puntos de integración entre componentes
- Validación de lógica de negocio específica

**Testing Basado en Propiedades:**
- Verificación de propiedades universales a través de muchas entradas generadas
- Cobertura exhaustiva de espacios de entrada
- Detección de casos límite no considerados
- Validación de invariantes del sistema

### Configuración de Testing Basado en Propiedades

**Biblioteca:** Hypothesis para Python
- Mínimo 100 iteraciones por test de propiedad
- Generadores personalizados para modelos de dominio
- Estrategias de generación para datos válidos e inválidos

**Etiquetado de Tests:**
Cada test de propiedad debe incluir un comentario que referencie la propiedad del diseño:
```python
# Feature: carddemo-api-migration, Property 1: Autenticación con credenciales válidas genera tokens JWT
@given(valid_user_credentials())
def test_valid_authentication_generates_jwt(credentials):
    # Test implementation
```

**Configuración de Testing:**
- Tests unitarios: pytest con fixtures para datos de prueba
- Tests de propiedades: Hypothesis con estrategias personalizadas
- Tests de integración: TestClient de FastAPI para endpoints completos
- Cobertura: Objetivo del 90% de cobertura de código

### Estrategias de Generación de Datos

**Usuarios y Credenciales:**
```python
@composite
def valid_user_credentials(draw):
    username = draw(text(min_size=3, max_size=50, alphabet=string.ascii_letters + string.digits))
    password = draw(text(min_size=8, max_size=128))
    return {"username": username, "password": password}
```

**Datos de Cuenta:**
```python
@composite
def account_data(draw):
    return {
        "first_name": draw(text(min_size=1, max_size=50, alphabet=string.ascii_letters)),
        "last_name": draw(text(min_size=1, max_size=50, alphabet=string.ascii_letters)),
        "phone": draw(one_of(none(), text(min_size=10, max_size=15, alphabet=string.digits))),
        # ... otros campos
    }
```

**Filtros de Transacciones:**
```python
@composite
def transaction_filters(draw):
    start_date = draw(one_of(none(), dates()))
    end_date = draw(one_of(none(), dates(min_value=start_date if start_date else date.min)))
    return TransactionFilters(
        start_date=start_date,
        end_date=end_date,
        # ... otros filtros
    )
```

### Testing de Seguridad

**Validación de Aislamiento de Datos:**
- Generación de múltiples usuarios con datos solapados
- Verificación de que cada usuario solo accede a sus datos
- Testing de intentos de acceso no autorizado

**Testing de Inyección:**
- Generación de payloads maliciosos (SQL injection, XSS)
- Verificación de sanitización apropiada
- Testing de validación de esquemas

**Testing de Rate Limiting:**
- Generación de múltiples peticiones concurrentes
- Verificación de aplicación de límites
- Testing de recuperación después de límites