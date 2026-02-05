# CardDemo API

API REST moderna para gestión de tarjetas de crédito, migrada desde la aplicación mainframe CardDemo COBOL.

## Características

- **Autenticación JWT**: Sistema seguro de autenticación con tokens
- **Gestión de Cuentas**: Ver y actualizar información de cuentas de usuario
- **Tarjetas de Crédito**: Listar y consultar tarjetas con información enmascarada
- **Transacciones**: Historial completo con filtros avanzados
- **Monitoreo**: Endpoints de salud del sistema
- **Seguridad**: Encriptación de datos sensibles y rate limiting

## Stack Tecnológico

- **FastAPI**: Framework web moderno y rápido
- **SQLite**: Base de datos ligera para MVP
- **SQLAlchemy**: ORM robusto con SQLModel
- **JWT**: Autenticación basada en tokens
- **Pydantic**: Validación de datos y serialización
- **Pytest + Hypothesis**: Testing unitario y basado en propiedades

## Instalación

1. **Clonar el repositorio**
   ```bash
   cd carddemo-api
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

5. **Ejecutar la aplicación**
   ```bash
   python main.py
   ```

## Uso

La API estará disponible en `http://localhost:8000`

- **Documentación interactiva**: `http://localhost:8000/docs`
- **Documentación alternativa**: `http://localhost:8000/redoc`
- **Verificación de salud**: `http://localhost:8000/health`

## Desarrollo

### Ejecutar tests
```bash
pytest
```

### Ejecutar con recarga automática
```bash
uvicorn main:app --reload
```

## Estructura del Proyecto

```
carddemo-api/
├── main.py              # Aplicación FastAPI principal
├── config.py            # Configuración de la aplicación
├── requirements.txt     # Dependencias Python
├── .env.example         # Ejemplo de variables de entorno
├── models/              # Modelos de datos (próximamente)
├── services/            # Lógica de negocio (próximamente)
├── routers/             # Endpoints de API (próximamente)
└── tests/               # Tests unitarios y de propiedades (próximamente)
```

## Licencia

Apache 2.0 - Mismo que el proyecto CardDemo original