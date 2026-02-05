"""
Tests de propiedades para características de seguridad avanzadas
"""
import pytest
import time
from hypothesis import given, strategies as st, settings
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from services.encryption_service import EncryptionService
from middleware.rate_limit import RateLimitMiddleware
from middleware.input_sanitizer import InputSanitizerMiddleware


class TestSecurityProperties:
    """Tests de propiedades para seguridad avanzada"""
    
    @given(
        card_numbers=st.lists(
            st.text(min_size=13, max_size=19, alphabet=st.characters(whitelist_categories=('Nd',))),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=10)
    def test_property_25_sensitive_data_encryption(self, card_numbers):
        """
        **Propiedad 25: Encriptación de datos sensibles**
        **Valida: Requisitos 8.1**
        
        Los números de tarjeta de crédito deben ser encriptados antes de almacenarse
        y desencriptados correctamente cuando se necesiten.
        """
        encryption_service = EncryptionService()
        
        for card_number in card_numbers:
            # Encriptar número de tarjeta
            encrypted = encryption_service.encrypt_card_number(card_number)
            
            # Verificar que está encriptado (diferente del original)
            assert encrypted != card_number, "El número encriptado debe ser diferente del original"
            assert len(encrypted) > len(card_number), "El número encriptado debe ser más largo"
            
            # Verificar que se puede desencriptar correctamente
            decrypted = encryption_service.decrypt_card_number(encrypted)
            assert decrypted == card_number, "El número desencriptado debe coincidir con el original"
            
            # Verificar que el enmascaramiento funciona
            masked = encryption_service.mask_card_number(encrypted)
            assert "*" in masked, "El número enmascarado debe contener asteriscos"
            # Verificar que los últimos dígitos están presentes de alguna forma
            last_digits = card_number[-4:]
            # Puede estar formateado con espacios, así que verificar dígito por dígito
            for digit in last_digits:
                assert digit in masked, f"El dígito {digit} debe estar visible en el número enmascarado"
    
    @given(
        plaintext_data=st.lists(
            st.text(min_size=1, max_size=100),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=10)
    def test_property_25_encryption_consistency(self, plaintext_data):
        """
        **Propiedad 25: Encriptación de datos sensibles - Consistencia**
        **Valida: Requisitos 8.1**
        
        La encriptación debe ser consistente y reversible para todos los datos.
        """
        encryption_service = EncryptionService()
        
        for data in plaintext_data:
            if not data.strip():  # Saltar strings vacíos
                continue
                
            # Encriptar datos
            encrypted = encryption_service.encrypt(data)
            
            # Verificar propiedades de encriptación
            assert encrypted != data, "Los datos encriptados deben ser diferentes"
            assert len(encrypted) > 0, "Los datos encriptados no deben estar vacíos"
            
            # Verificar que se puede desencriptar
            decrypted = encryption_service.decrypt(encrypted)
            assert decrypted == data, "Los datos desencriptados deben coincidir"
            
            # Verificar que encriptar el mismo dato múltiples veces da resultados diferentes (por seguridad)
            encrypted2 = encryption_service.encrypt(data)
            assert encrypted != encrypted2, "La encriptación debe usar nonces aleatorios para seguridad"
            
            # Pero ambos deben desencriptar al mismo valor
            decrypted2 = encryption_service.decrypt(encrypted2)
            assert decrypted2 == data, "Ambas encriptaciones deben desencriptar al mismo valor"
    
    def test_property_26_rate_limiting_enforcement(self):
        """
        **Propiedad 26: Rate limiting para prevención de abuso**
        **Valida: Requisitos 8.3**
        
        El sistema debe limitar el número de requests por IP para prevenir abuso.
        """
        # Crear app de prueba con rate limiting muy restrictivo
        test_app = FastAPI()
        test_app.add_middleware(RateLimitMiddleware, calls_per_minute=3, burst_limit=2)
        
        @test_app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        client = TestClient(test_app)
        
        # Hacer requests hasta alcanzar el límite
        successful_requests = 0
        rate_limited = False
        
        for i in range(5):  # Intentar 5 requests
            response = client.get("/test")
            
            if response.status_code == 200:
                successful_requests += 1
                # Verificar headers de rate limit
                assert "X-RateLimit-Limit-Minute" in response.headers
                assert "X-RateLimit-Remaining-Minute" in response.headers
            elif response.status_code == 429:
                rate_limited = True
                # Verificar respuesta de rate limit
                data = response.json()
                assert "error" in data
                assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
                assert "Retry-After" in response.headers
                break
        
        # Debe haber al menos algunos requests exitosos y luego rate limiting
        assert successful_requests > 0, "Debe permitir algunos requests"
        assert rate_limited, "Debe aplicar rate limiting después del límite"
    
    def test_property_26_rate_limiting_per_ip(self):
        """
        **Propiedad 26: Rate limiting por IP**
        **Valida: Requisitos 8.3**
        
        El rate limiting debe ser por IP, no global.
        """
        test_app = FastAPI()
        test_app.add_middleware(RateLimitMiddleware, calls_per_minute=2, burst_limit=1)
        
        @test_app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        client = TestClient(test_app)
        
        # Simular requests desde diferentes IPs usando headers
        ip1_headers = {"X-Forwarded-For": "192.168.1.1"}
        ip2_headers = {"X-Forwarded-For": "192.168.1.2"}
        
        # IP1 hace requests hasta el límite
        response1 = client.get("/test", headers=ip1_headers)
        assert response1.status_code == 200
        
        response2 = client.get("/test", headers=ip1_headers)
        # Puede ser 200 o 429 dependiendo del timing
        
        # IP2 debe poder hacer requests independientemente
        response3 = client.get("/test", headers=ip2_headers)
        assert response3.status_code == 200, "Diferentes IPs deben tener límites independientes"
    
    @given(
        malicious_inputs=st.lists(
            st.one_of(
                st.just("<script>alert('xss')</script>"),
                st.just("'; DROP TABLE users; --"),
                st.just("javascript:alert('xss')"),
                st.just("<img src=x onerror=alert('xss')>"),
                st.just("UNION SELECT * FROM users"),
                st.just("OR 1=1"),
                st.text().filter(lambda x: any(pattern in x.lower() for pattern in ['<script', 'javascript:', 'drop table', 'union select']))
            ),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=10)
    def test_property_28_input_sanitization(self, malicious_inputs):
        """
        **Propiedad 28: Sanitización de entrada para prevenir inyección**
        **Valida: Requisitos 8.5**
        
        Todas las entradas deben ser sanitizadas para prevenir ataques de inyección.
        """
        encryption_service = EncryptionService()
        
        for malicious_input in malicious_inputs:
            sanitized = encryption_service.sanitize_input(malicious_input)
            
            # Verificar que se removieron patrones peligrosos
            dangerous_patterns = [
                '<script', '</script>',
                'javascript:', 'vbscript:',
                'drop table', 'delete from', 'insert into',
                'union select', 'or 1=1'
            ]
            
            sanitized_lower = sanitized.lower()
            for pattern in dangerous_patterns:
                assert pattern not in sanitized_lower, f"Patrón peligroso '{pattern}' no fue removido"
            
            # Verificar que caracteres especiales fueron escapados
            assert '<' not in sanitized or '&lt;' in sanitized, "< debe ser escapado"
            assert '>' not in sanitized or '&gt;' in sanitized, "> debe ser escapado"
            
            # La entrada sanitizada puede estar vacía si era completamente maliciosa
            # Esto es comportamiento esperado para seguridad
            if malicious_input.strip() and not any(pattern in malicious_input.lower() for pattern in ['or 1=1', 'drop table', 'union select']):
                assert sanitized.strip(), "La sanitización no debe vaciar entrada no maliciosa"
    
    @given(
        nested_data=st.recursive(
            st.one_of(
                st.text(),
                st.integers(),
                st.booleans()
            ),
            lambda children: st.one_of(
                st.lists(children, max_size=3),
                st.dictionaries(st.text(max_size=10), children, max_size=3)
            ),
            max_leaves=10
        )
    )
    @settings(max_examples=10)
    def test_property_28_recursive_sanitization(self, nested_data):
        """
        **Propiedad 28: Sanitización recursiva de estructuras complejas**
        **Valida: Requisitos 8.5**
        
        La sanitización debe funcionar recursivamente en estructuras de datos complejas.
        """
        from middleware.input_sanitizer import InputSanitizerMiddleware
        
        middleware = InputSanitizerMiddleware(None)
        sanitized = middleware._sanitize_data(nested_data)
        
        # Verificar que la estructura se mantiene
        assert type(sanitized) == type(nested_data), "El tipo de datos debe mantenerse"
        
        # Verificar sanitización recursiva
        def check_sanitized(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(key, str):
                        assert '<script' not in key.lower(), "Claves deben estar sanitizadas"
                    check_sanitized(value)
            elif isinstance(data, list):
                for item in data:
                    check_sanitized(item)
            elif isinstance(data, str):
                assert '<script' not in data.lower(), "Strings deben estar sanitizados"
        
        check_sanitized(sanitized)
    
    def test_property_encryption_key_security(self):
        """
        **Propiedad 25: Seguridad de claves de encriptación**
        **Valida: Requisitos 8.1**
        
        Las claves de encriptación deben ser seguras y no predecibles.
        """
        # Crear múltiples servicios de encriptación
        service1 = EncryptionService()
        service2 = EncryptionService()
        
        test_data = "sensitive_data_123"
        
        # Encriptar con ambos servicios
        encrypted1 = service1.encrypt(test_data)
        encrypted2 = service2.encrypt(test_data)
        
        # Los resultados deben ser diferentes (por el nonce aleatorio) pero ambos válidos
        assert encrypted1 != encrypted2, "Encriptaciones deben ser diferentes por seguridad"
        
        # Pero diferentes de los datos originales
        assert encrypted1 != test_data
        assert encrypted2 != test_data
        
        # Y deben poder desencriptar correctamente
        assert service1.decrypt(encrypted1) == test_data
        assert service2.decrypt(encrypted2) == test_data
    
    def test_property_rate_limiting_headers_consistency(self):
        """
        **Propiedad 26: Consistencia de headers de rate limiting**
        **Valida: Requisitos 8.3**
        
        Los headers de rate limiting deben ser consistentes y informativos.
        """
        test_app = FastAPI()
        test_app.add_middleware(RateLimitMiddleware, calls_per_minute=10, calls_per_hour=100)
        
        @test_app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        client = TestClient(test_app)
        
        response = client.get("/test")
        assert response.status_code == 200
        
        # Verificar headers requeridos
        required_headers = [
            "X-RateLimit-Limit-Minute",
            "X-RateLimit-Remaining-Minute", 
            "X-RateLimit-Limit-Hour",
            "X-RateLimit-Remaining-Hour",
            "X-RateLimit-Reset"
        ]
        
        for header in required_headers:
            assert header in response.headers, f"Header {header} debe estar presente"
            assert response.headers[header].isdigit(), f"Header {header} debe ser numérico"
        
        # Verificar valores lógicos
        limit_minute = int(response.headers["X-RateLimit-Limit-Minute"])
        remaining_minute = int(response.headers["X-RateLimit-Remaining-Minute"])
        
        assert limit_minute == 10, "Límite por minuto debe coincidir con configuración"
        assert remaining_minute <= limit_minute, "Remaining debe ser <= limit"
        assert remaining_minute >= 0, "Remaining no puede ser negativo"