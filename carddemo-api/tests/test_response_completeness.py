"""
Tests de propiedades para completitud de respuestas de API
"""
import pytest
from hypothesis import given, strategies as st, settings
from fastapi.testclient import TestClient
from unittest.mock import patch
from decimal import Decimal
from datetime import datetime, timezone

from main import app
from services.response_validator import get_response_validator
from models.api_models import CardResponse, TransactionResponse, AccountResponse
from models.database_models import User, Account, CreditCard, Transaction


class TestResponseCompletenessProperties:
    """Tests de propiedades para completitud de respuestas"""
    
    def test_property_12_card_response_completeness(self):
        """
        **Propiedad 12: Completitud de respuestas de API - Tarjetas**
        **Valida: Requisitos 3.4**
        
        Todas las respuestas de tarjetas deben incluir campos requeridos:
        estado, tipo, información de expiración.
        """
        client = TestClient(app)
        validator = get_response_validator()
        
        # Crear datos de prueba para tarjeta
        card_data = {
            "id": 1,
            "masked_card_number": "**** **** **** 1234",
            "card_type": "VISA",
            "expiry_month": 12,
            "expiry_year": 2025,
            "status": "ACTIVE",
            "credit_limit": Decimal("5000.00"),
            "available_credit": Decimal("4200.00"),
            "created_at": datetime.now(timezone.utc)
        }
        
        # Validar completitud
        validation_result = validator.validate_card_response(card_data)
        
        # Verificar que la respuesta está completa
        assert validation_result['is_complete'], f"Respuesta de tarjeta incompleta: {validation_result['missing_fields']}"
        assert len(validation_result['missing_fields']) == 0, "No debe haber campos faltantes"
        assert len(validation_result['empty_fields']) == 0, "No debe haber campos vacíos"
        
        # Verificar campos específicos requeridos por Requisito 3.4
        required_fields = {'status', 'card_type', 'expiry_month', 'expiry_year'}
        present_fields = set(validation_result['present_fields'])
        
        assert required_fields.issubset(present_fields), f"Campos requeridos faltantes: {required_fields - present_fields}"
        
        # Verificar completitud del 100%
        assert validation_result['completeness_percentage'] == 100.0, "Debe tener 100% de completitud"
    
    def test_property_12_transaction_response_completeness(self):
        """
        **Propiedad 12: Completitud de respuestas de API - Transacciones**
        **Valida: Requisitos 4.4**
        
        Todas las respuestas de transacciones deben incluir campos requeridos:
        monto, fecha, comerciante, estado.
        """
        validator = get_response_validator()
        
        # Crear datos de prueba para transacción
        transaction_data = {
            "id": 1,
            "transaction_date": datetime.now(timezone.utc),
            "merchant_name": "Amazon",
            "amount": Decimal("89.99"),
            "transaction_type": "PURCHASE",
            "status": "COMPLETED",
            "description": "Online purchase",
            "created_at": datetime.now(timezone.utc)
        }
        
        # Validar completitud
        validation_result = validator.validate_transaction_response(transaction_data)
        
        # Verificar que la respuesta está completa
        assert validation_result['is_complete'], f"Respuesta de transacción incompleta: {validation_result['missing_fields']}"
        assert len(validation_result['missing_fields']) == 0, "No debe haber campos faltantes"
        assert len(validation_result['empty_fields']) == 0, "No debe haber campos vacíos"
        
        # Verificar campos específicos requeridos por Requisito 4.4
        required_fields = {'amount', 'transaction_date', 'merchant_name', 'status'}
        present_fields = set(validation_result['present_fields'])
        
        assert required_fields.issubset(present_fields), f"Campos requeridos faltantes: {required_fields - present_fields}"
        
        # Verificar completitud del 100%
        assert validation_result['completeness_percentage'] == 100.0, "Debe tener 100% de completitud"
    
    @given(
        missing_fields=st.lists(
            st.sampled_from(['status', 'card_type', 'expiry_month', 'expiry_year']),
            min_size=1,
            max_size=3,
            unique=True
        )
    )
    @settings(max_examples=10)
    def test_property_12_incomplete_card_response_detection(self, missing_fields):
        """
        **Propiedad 12: Detección de respuestas incompletas - Tarjetas**
        **Valida: Requisitos 3.4**
        
        El validador debe detectar cuando faltan campos requeridos en respuestas de tarjetas.
        """
        validator = get_response_validator()
        
        # Crear datos completos de tarjeta
        complete_card_data = {
            "id": 1,
            "masked_card_number": "**** **** **** 1234",
            "card_type": "VISA",
            "expiry_month": 12,
            "expiry_year": 2025,
            "status": "ACTIVE",
            "credit_limit": Decimal("5000.00"),
            "available_credit": Decimal("4200.00"),
            "created_at": datetime.now(timezone.utc)
        }
        
        # Remover campos específicos para simular respuesta incompleta
        incomplete_card_data = complete_card_data.copy()
        for field in missing_fields:
            if field in incomplete_card_data:
                del incomplete_card_data[field]
        
        # Validar completitud
        validation_result = validator.validate_card_response(incomplete_card_data)
        
        # Verificar que se detecta la incompletitud
        assert not validation_result['is_complete'], "Debe detectar respuesta incompleta"
        assert len(validation_result['missing_fields']) > 0, "Debe reportar campos faltantes"
        
        # Verificar que los campos faltantes son los esperados
        detected_missing = set(validation_result['missing_fields'])
        expected_missing = set(missing_fields)
        
        assert expected_missing.issubset(detected_missing), f"Debe detectar campos faltantes: {expected_missing}"
        
        # Verificar que la completitud es menor al 100%
        assert validation_result['completeness_percentage'] < 100.0, "Completitud debe ser menor al 100%"
    
    @given(
        empty_fields=st.lists(
            st.sampled_from(['merchant_name', 'status']),
            min_size=1,
            max_size=2,
            unique=True
        )
    )
    @settings(max_examples=10)
    def test_property_12_empty_field_detection(self, empty_fields):
        """
        **Propiedad 12: Detección de campos vacíos**
        **Valida: Requisitos 4.4**
        
        El validador debe detectar cuando campos requeridos están vacíos o son None.
        """
        validator = get_response_validator()
        
        # Crear datos de transacción con campos vacíos
        transaction_data = {
            "id": 1,
            "transaction_date": datetime.now(timezone.utc),
            "merchant_name": "Amazon",
            "amount": Decimal("89.99"),
            "transaction_type": "PURCHASE",
            "status": "COMPLETED"
        }
        
        # Hacer campos específicos vacíos
        for field in empty_fields:
            if field in transaction_data:
                transaction_data[field] = "" if field == "merchant_name" else None
        
        # Validar completitud
        validation_result = validator.validate_transaction_response(transaction_data)
        
        # Verificar que se detectan campos vacíos
        if empty_fields:
            assert not validation_result['is_complete'], "Debe detectar campos vacíos"
            assert len(validation_result['empty_fields']) > 0, "Debe reportar campos vacíos"
            
            detected_empty = set(validation_result['empty_fields'])
            expected_empty = set(empty_fields)
            
            assert expected_empty.issubset(detected_empty), f"Debe detectar campos vacíos: {expected_empty}"
    
    def test_property_12_list_response_completeness(self):
        """
        **Propiedad 12: Completitud de respuestas de lista**
        **Valida: Requisitos 3.4, 4.4**
        
        Las respuestas de lista deben validar completitud de todos los elementos.
        """
        validator = get_response_validator()
        
        # Crear lista de tarjetas con diferentes niveles de completitud
        cards_data = [
            {
                "id": 1,
                "masked_card_number": "**** **** **** 1234",
                "card_type": "VISA",
                "expiry_month": 12,
                "expiry_year": 2025,
                "status": "ACTIVE",
                "credit_limit": Decimal("5000.00"),
                "available_credit": Decimal("4200.00"),
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": 2,
                "masked_card_number": "**** **** **** 5678",
                "card_type": "MASTERCARD",
                "expiry_month": 6,
                "expiry_year": 2026,
                # Falta 'status' - respuesta incompleta
                "credit_limit": Decimal("3000.00"),
                "available_credit": Decimal("2800.00"),
                "created_at": datetime.now(timezone.utc)
            }
        ]
        
        # Validar completitud de lista
        validation_result = validator.validate_list_response(cards_data, 'card')
        
        # Verificar estadísticas de completitud
        assert validation_result['total_items'] == 2, "Debe contar todos los elementos"
        assert validation_result['complete_items'] == 1, "Debe identificar elementos completos"
        assert validation_result['incomplete_items'] == 1, "Debe identificar elementos incompletos"
        assert not validation_result['is_complete'], "Lista no debe estar completa"
        assert validation_result['completeness_percentage'] == 50.0, "Debe calcular porcentaje correcto"
        
        # Verificar detalles de validación
        assert len(validation_result['validation_details']) == 2, "Debe tener detalles para cada elemento"
        assert validation_result['validation_details'][0]['is_complete'], "Primer elemento debe estar completo"
        assert not validation_result['validation_details'][1]['is_complete'], "Segundo elemento debe estar incompleto"
    
    def test_property_12_pydantic_model_validation(self):
        """
        **Propiedad 12: Validación con modelos Pydantic**
        **Valida: Requisitos 3.4, 4.4**
        
        La validación debe funcionar con instancias de modelos Pydantic.
        """
        validator = get_response_validator()
        
        # Crear instancia de modelo Pydantic para tarjeta
        card_response = CardResponse(
            id=1,
            masked_card_number="**** **** **** 1234",
            card_type="VISA",
            expiry_month=12,
            expiry_year=2025,
            status="ACTIVE",
            credit_limit=Decimal("5000.00"),
            available_credit=Decimal("4200.00"),
            created_at=datetime.now(timezone.utc)
        )
        
        # Validar usando modelo Pydantic
        validation_result = validator.validate_pydantic_model_completeness(card_response, 'card')
        
        # Verificar que la validación funciona con modelos Pydantic
        assert validation_result['is_complete'], "Modelo Pydantic debe estar completo"
        assert validation_result['completeness_percentage'] == 100.0, "Debe tener 100% de completitud"
        assert len(validation_result['missing_fields']) == 0, "No debe haber campos faltantes"
    
    def test_property_12_schema_validation_summary(self):
        """
        **Propiedad 12: Resumen de validación de esquema**
        **Valida: Requisitos 3.4, 4.4**
        
        El validador debe proporcionar resúmenes de validación para cada tipo de respuesta.
        """
        validator = get_response_validator()
        
        # Obtener resumen para tarjetas
        card_summary = validator.get_schema_validation_summary('card')
        
        # Verificar estructura del resumen
        assert card_summary['response_type'] == 'card', "Debe identificar tipo correcto"
        assert 'required_fields' in card_summary, "Debe incluir campos requeridos"
        assert 'validation_rules' in card_summary, "Debe incluir reglas de validación"
        assert 'requirements_mapping' in card_summary, "Debe incluir mapeo de requisitos"
        
        # Verificar campos requeridos específicos
        required_fields = set(card_summary['required_fields'])
        expected_fields = {'status', 'card_type', 'expiry_month', 'expiry_year'}
        
        assert expected_fields.issubset(required_fields), "Debe incluir campos requeridos por Requisito 3.4"
        
        # Obtener resumen para transacciones
        transaction_summary = validator.get_schema_validation_summary('transaction')
        
        # Verificar campos requeridos para transacciones
        transaction_required = set(transaction_summary['required_fields'])
        expected_transaction_fields = {'amount', 'transaction_date', 'merchant_name', 'status'}
        
        assert expected_transaction_fields.issubset(transaction_required), "Debe incluir campos requeridos por Requisito 4.4"
    
    def test_property_12_requirements_mapping_accuracy(self):
        """
        **Propiedad 12: Precisión del mapeo de requisitos**
        **Valida: Requisitos 3.4, 4.4**
        
        El mapeo de campos a requisitos debe ser preciso y completo.
        """
        validator = get_response_validator()
        
        # Verificar mapeo para tarjetas
        card_summary = validator.get_schema_validation_summary('card')
        card_mapping = card_summary['requirements_mapping']
        
        # Verificar mapeos específicos del Requisito 3.4
        assert 'status' in card_mapping, "Debe mapear campo status"
        assert 'Requisito 3.4' in card_mapping['status'], "Status debe mapear a Requisito 3.4"
        
        assert 'card_type' in card_mapping, "Debe mapear campo card_type"
        assert 'Requisito 3.4' in card_mapping['card_type'], "Card_type debe mapear a Requisito 3.4"
        
        assert 'expiry_month' in card_mapping, "Debe mapear campo expiry_month"
        assert 'Requisito 3.4' in card_mapping['expiry_month'], "Expiry_month debe mapear a Requisito 3.4"
        
        # Verificar mapeo para transacciones
        transaction_summary = validator.get_schema_validation_summary('transaction')
        transaction_mapping = transaction_summary['requirements_mapping']
        
        # Verificar mapeos específicos del Requisito 4.4
        assert 'amount' in transaction_mapping, "Debe mapear campo amount"
        assert 'Requisito 4.4' in transaction_mapping['amount'], "Amount debe mapear a Requisito 4.4"
        
        assert 'merchant_name' in transaction_mapping, "Debe mapear campo merchant_name"
        assert 'Requisito 4.4' in transaction_mapping['merchant_name'], "Merchant_name debe mapear a Requisito 4.4"
    
    def test_property_12_empty_list_handling(self):
        """
        **Propiedad 12: Manejo de listas vacías**
        **Valida: Requisitos 3.4, 4.4**
        
        Las listas vacías deben considerarse completas (100% de completitud).
        """
        validator = get_response_validator()
        
        # Validar lista vacía
        validation_result = validator.validate_list_response([], 'card')
        
        # Verificar que lista vacía se considera completa
        assert validation_result['is_complete'], "Lista vacía debe considerarse completa"
        assert validation_result['total_items'] == 0, "Debe contar 0 elementos"
        assert validation_result['complete_items'] == 0, "Debe tener 0 elementos completos"
        assert validation_result['incomplete_items'] == 0, "Debe tener 0 elementos incompletos"
        assert validation_result['completeness_percentage'] == 100.0, "Lista vacía debe tener 100% completitud"
        assert len(validation_result['validation_details']) == 0, "No debe haber detalles de validación"