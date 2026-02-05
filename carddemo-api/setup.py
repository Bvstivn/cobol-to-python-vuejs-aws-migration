"""
Script de configuración inicial para CardDemo API
"""
import subprocess
import sys
import os


def install_dependencies():
    """Instalar dependencias de requirements.txt"""
    print("📦 Instalando dependencias...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False


def create_env_file():
    """Crear archivo .env si no existe"""
    if not os.path.exists(".env"):
        print("📝 Creando archivo .env...")
        try:
            with open(".env.example", "r") as example:
                content = example.read()
            with open(".env", "w") as env_file:
                env_file.write(content)
            print("✅ Archivo .env creado")
        except Exception as e:
            print(f"❌ Error creando .env: {e}")
    else:
        print("ℹ️  Archivo .env ya existe")


def test_configuration():
    """Probar que la configuración funciona"""
    print("🧪 Probando configuración...")
    try:
        from config import settings
        print(f"✅ Configuración cargada: {settings.app_name} v{settings.app_version}")
        return True
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False


def main():
    """Función principal de configuración"""
    print("🚀 Configurando CardDemo API...")
    
    # Instalar dependencias
    if not install_dependencies():
        return False
    
    # Crear archivo .env
    create_env_file()
    
    # Probar configuración
    if not test_configuration():
        return False
    
    print("\n🎉 ¡Configuración completada exitosamente!")
    print("\nPróximos pasos:")
    print("1. Revisar y ajustar configuración en .env")
    print("2. Ejecutar: python main.py")
    print("3. Abrir: http://localhost:8000")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)