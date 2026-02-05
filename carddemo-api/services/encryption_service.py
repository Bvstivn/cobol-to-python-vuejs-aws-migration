"""
Servicio de encriptación para datos sensibles en CardDemo API
"""
import base64
import os
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)


class EncryptionService:
    """Servicio para encriptar y desencriptar datos sensibles"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Inicializar servicio de encriptación
        
        Args:
            encryption_key: Clave de encriptación. Si no se proporciona, se genera una nueva.
        """
        if encryption_key:
            # Usar clave proporcionada
            self._key = encryption_key.encode()
        else:
            # Generar clave desde variable de entorno o crear una nueva
            env_key = os.getenv("ENCRYPTION_KEY")
            if env_key:
                self._key = env_key.encode()
            else:
                # En desarrollo, generar clave temporal
                # En producción, esto debería venir de un gestor de secretos
                self._key = Fernet.generate_key()
                logger.warning("Using temporary encryption key. Set ENCRYPTION_KEY environment variable for production.")
        
        # Crear instancia de Fernet para encriptación simétrica
        self._fernet = Fernet(self._derive_key(self._key))
    
    def _derive_key(self, password: bytes) -> bytes:
        """
        Derivar clave de encriptación usando PBKDF2
        
        Args:
            password: Contraseña base
            
        Returns:
            Clave derivada para Fernet
        """
        # Salt fijo para consistencia (en producción debería ser único por instalación)
        salt = b'carddemo_salt_2024'
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt(self, data: str) -> str:
        """
        Encriptar datos sensibles
        
        Args:
            data: Datos a encriptar
            
        Returns:
            Datos encriptados en formato base64
        """
        if not data:
            return data
        
        try:
            encrypted_data = self._fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise ValueError("Failed to encrypt data")
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Desencriptar datos
        
        Args:
            encrypted_data: Datos encriptados en formato base64
            
        Returns:
            Datos desencriptados
        """
        if not encrypted_data:
            return encrypted_data
        
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self._fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise ValueError("Failed to decrypt data")
    
    def encrypt_card_number(self, card_number: str) -> str:
        """
        Encriptar número de tarjeta de crédito
        
        Args:
            card_number: Número de tarjeta sin formato
            
        Returns:
            Número de tarjeta encriptado
        """
        # Remover espacios y caracteres no numéricos
        clean_number = ''.join(filter(str.isdigit, card_number))
        return self.encrypt(clean_number)
    
    def decrypt_card_number(self, encrypted_card_number: str) -> str:
        """
        Desencriptar número de tarjeta de crédito
        
        Args:
            encrypted_card_number: Número de tarjeta encriptado
            
        Returns:
            Número de tarjeta desencriptado
        """
        return self.decrypt(encrypted_card_number)
    
    def mask_card_number(self, card_number: str) -> str:
        """
        Enmascarar número de tarjeta para mostrar
        
        Args:
            card_number: Número de tarjeta (puede estar encriptado)
            
        Returns:
            Número de tarjeta enmascarado (ej: **** **** **** 1234)
        """
        try:
            # Si está encriptado, desencriptar primero
            if len(card_number) > 20:  # Probablemente encriptado
                decrypted = self.decrypt_card_number(card_number)
            else:
                decrypted = card_number
            
            # Limpiar número
            clean_number = ''.join(filter(str.isdigit, decrypted))
            
            if len(clean_number) < 4:
                return "*" * len(clean_number)
            
            # Mostrar solo los últimos 4 dígitos
            masked = "*" * (len(clean_number) - 4) + clean_number[-4:]
            
            # Formatear con espacios cada 4 dígitos
            formatted = ' '.join([masked[i:i+4] for i in range(0, len(masked), 4)])
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error masking card number: {e}")
            return "**** **** **** ****"
    
    def sanitize_input(self, input_data: str) -> str:
        """
        Sanitizar entrada para prevenir inyección
        
        Args:
            input_data: Datos de entrada
            
        Returns:
            Datos sanitizados
        """
        if not input_data:
            return input_data
        
        # Lista de patrones peligrosos
        dangerous_patterns = [
            '<script', '</script>',
            'javascript:', 'vbscript:',
            'onload=', 'onerror=', 'onclick=',
            'eval(', 'exec(',
            'DROP TABLE', 'DELETE FROM', 'INSERT INTO', 'UPDATE SET',
            '--', '/*', '*/',
            'UNION SELECT', 'OR 1=1', 'AND 1=1'
        ]
        
        sanitized = input_data
        
        # Remover patrones peligrosos (case insensitive)
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern.lower(), '')
            sanitized = sanitized.replace(pattern.upper(), '')
            sanitized = sanitized.replace(pattern.capitalize(), '')
        
        # Escapar caracteres especiales
        sanitized = sanitized.replace('<', '&lt;')
        sanitized = sanitized.replace('>', '&gt;')
        sanitized = sanitized.replace('"', '&quot;')
        sanitized = sanitized.replace("'", '&#x27;')
        sanitized = sanitized.replace('&', '&amp;')
        
        return sanitized.strip()


# Instancia global del servicio de encriptación
_encryption_service = None


def get_encryption_service() -> EncryptionService:
    """
    Obtener instancia global del servicio de encriptación
    
    Returns:
        Instancia de EncryptionService
    """
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service