"""
Script de prueba para verificar que la configuración inicial funciona correctamente
"""
import sys
from fastapi.testclient import TestClient


def test_basic_imports():
    """Probar que las importaciones básicas funcionan"""
    try:
        import fastapi
        import sqlalchemy
        import pydantic
        import bcrypt
        print("✅ Todas las dependencias principales importadas correctamente")
        return True
    except ImportError as e:
        print(f"❌ Error importando dependencias: {e}")
        return False


def test_config():
    """Probar que la configuración se carga correctamente"""
    try:
        from config import settings
        print(f"✅ Configuración cargada: {settings.app_name} v{settings.app_version}")
        return True
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False


def test_fastapi_app():
    """Probar que la aplicación FastAPI funciona"""
    try:
        from main import app
        client = TestClient(app)
        
        # Probar endpoint raíz
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✅ Endpoint raíz funciona: {data['message']}")
        
        # Probar endpoint de salud
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✅ Endpoint de salud funciona: {data['status']}")
        
        return True
    except Exception as e:
        print(f"❌ Error probando FastAPI: {e}")
        return False


def main():
    """Función principal de pruebas"""
    print("🧪 Ejecutando pruebas de configuración inicial...\n")
    
    tests = [
        ("Importaciones básicas", test_basic_imports),
        ("Configuración", test_config),
        ("Aplicación FastAPI", test_fastapi_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"🔍 Probando {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 Resultados: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! La configuración inicial está completa.")
        print("\n📋 Próximos pasos:")
        print("1. Ejecutar: python main.py")
        print("2. Abrir: http://localhost:8000")
        print("3. Ver documentación: http://localhost:8000/docs")
        return True
    else:
        print("❌ Algunas pruebas fallaron. Revisar la configuración.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)