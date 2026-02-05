"""
Configuración de la aplicación CardDemo API
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic Settings"""
    
    # Información de la aplicación
    app_name: str = "CardDemo API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Base de datos
    database_url: str = "sqlite:///./carddemo.db"
    
    # JWT Configuration
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Configuración de seguridad
    bcrypt_rounds: int = 12
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()