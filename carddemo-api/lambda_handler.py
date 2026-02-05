"""
Lambda Handler para FastAPI con Mangum
Adapta la aplicación FastAPI para ejecutarse en AWS Lambda
"""
from mangum import Mangum
from main import app

# Mangum convierte las peticiones de API Gateway a formato ASGI
# y las respuestas ASGI a formato API Gateway
handler = Mangum(app, lifespan="off")
