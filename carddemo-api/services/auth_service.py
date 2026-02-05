"""
Servicio de autenticación para CardDemo API
"""
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from sqlmodel import Session, select

from config import settings
from models.database_models import User


class AuthService:
    """Servicio para manejo de autenticación y contraseñas"""
    
    def __init__(self):
        self.bcrypt_rounds = settings.bcrypt_rounds
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    def hash_password(self, password: str) -> str:
        """Hashear contraseña usando bcrypt"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña contra hash"""
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    def authenticate_user(self, session: Session, username: str, password: str) -> Optional[User]:
        """
        Autenticar usuario con credenciales
        
        Args:
            session: Sesión de base de datos
            username: Nombre de usuario
            password: Contraseña en texto plano
            
        Returns:
            Usuario autenticado o None si las credenciales son inválidas
        """
        # Buscar usuario por username
        statement = select(User).where(User.username == username, User.is_active == True)
        user = session.exec(statement).first()
        
        if not user:
            return None
        
        # Verificar contraseña
        if not self.verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def create_access_token(self, user_data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Crear token JWT de acceso
        
        Args:
            user_data: Datos del usuario para incluir en el token
            expires_delta: Tiempo de expiración personalizado
            
        Returns:
            Token JWT codificado
        """
        to_encode = user_data.copy()
        
        now = datetime.now(timezone.utc)
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "iat": now})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """
        Verificar y decodificar token JWT
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            Payload del token si es válido, None si es inválido
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verificar que el token no haya expirado
            exp = payload.get("exp")
            if exp is None:
                return None
            
            # Convertir timestamp a datetime con timezone UTC
            if isinstance(exp, (int, float)):
                exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
            else:
                # Si exp ya es un datetime, asegurar que tenga timezone UTC
                exp_datetime = exp.replace(tzinfo=timezone.utc) if exp.tzinfo is None else exp
            
            now = datetime.now(timezone.utc)
            if now >= exp_datetime:
                return None
            
            return payload
        except JWTError:
            return None
    
    def get_current_user(self, session: Session, token: str) -> Optional[User]:
        """
        Obtener usuario actual desde token JWT
        
        Args:
            session: Sesión de base de datos
            token: Token JWT
            
        Returns:
            Usuario actual o None si el token es inválido
        """
        payload = self.verify_token(token)
        if payload is None:
            return None
        
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return None
        
        # Buscar usuario en base de datos
        statement = select(User).where(User.id == user_id, User.is_active == True)
        user = session.exec(statement).first()
        
        return user
    
    def create_user_token_data(self, user: User) -> dict:
        """
        Crear datos para incluir en el token JWT
        
        Args:
            user: Usuario autenticado
            
        Returns:
            Diccionario con datos del usuario para el token
        """
        return {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active
        }