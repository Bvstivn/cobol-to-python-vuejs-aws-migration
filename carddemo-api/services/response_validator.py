"""
Validador de completitud de respuestas de API para CardDemo
"""
from typing import Dict, List, Any, Optional, Set
from pydantic import BaseModel
from models.api_models import CardResponse, TransactionResponse, AccountResponse
import logging

logger = logging.getLogger(__name__)


class ResponseCompletenessValidator:
    """Validador para asegurar completitud de respuestas de API"""
    
    # Campos requeridos por tipo de respuesta según requisitos
    REQUIRED_FIELDS = {
        'card': {
            'status',           # Requisito 3.4: estado de tarjeta
            'card_type',        # Requisito 3.4: tipo de tarjeta
            'expiry_month',     # Requisito 3.4: información de expiración
            'expiry_year',      # Requisito 3.4: información de expiración
            'masked_card_number',  # Seguridad: número enmascarado
            'id',              # Identificación única
            'credit_limit',    # Información financiera
            'available_credit' # Información financiera
        },
        'transaction': {
            'amount',           # Requisito 4.4: monto de transacción
            'transaction_date', # Requisito 4.4: fecha
            'merchant_name',    # Requisito 4.4: comerciante
            'status',          # Requisito 4.4: información de estado
            'transaction_type', # Tipo de transacción
            'id'               # Identificación única
        },
        'account': {
            'id',              # Identificación única
            'account_number',  # Número de cuenta
            'first_name',      # Información personal
            'last_name',       # Información personal
            'phone',           # Información de contacto
            'address',         # Información de dirección
            'city',            # Información de dirección
            'state',           # Información de dirección
            'zip_code'         # Información de dirección
        }
    }
    
    def __init__(self):
        """Inicializar validador de completitud"""
        self.validation_errors = []
    
    def validate_card_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validar completitud de respuesta de tarjeta
        
        Args:
            response_data: Datos de respuesta de tarjeta
            
        Returns:
            Resultado de validación con campos faltantes si los hay
        """
        return self._validate_response(response_data, 'card')
    
    def validate_transaction_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validar completitud de respuesta de transacción
        
        Args:
            response_data: Datos de respuesta de transacción
            
        Returns:
            Resultado de validación con campos faltantes si los hay
        """
        return self._validate_response(response_data, 'transaction')
    
    def validate_account_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validar completitud de respuesta de cuenta
        
        Args:
            response_data: Datos de respuesta de cuenta
            
        Returns:
            Resultado de validación con campos faltantes si los hay
        """
        return self._validate_response(response_data, 'account')
    
    def _validate_response(self, response_data: Dict[str, Any], response_type: str) -> Dict[str, Any]:
        """
        Validar completitud de respuesta genérica
        
        Args:
            response_data: Datos de respuesta
            response_type: Tipo de respuesta ('card', 'transaction', 'account')
            
        Returns:
            Resultado de validación
        """
        required_fields = self.REQUIRED_FIELDS.get(response_type, set())
        present_fields = set(response_data.keys())
        missing_fields = required_fields - present_fields
        
        # Verificar campos con valores None o vacíos
        empty_fields = set()
        for field in required_fields:
            if field in response_data:
                value = response_data[field]
                if value is None or (isinstance(value, str) and not value.strip()):
                    empty_fields.add(field)
        
        validation_result = {
            'is_complete': len(missing_fields) == 0 and len(empty_fields) == 0,
            'response_type': response_type,
            'required_fields': list(required_fields),
            'present_fields': list(present_fields),
            'missing_fields': list(missing_fields),
            'empty_fields': list(empty_fields),
            'total_required': len(required_fields),
            'total_present': len(present_fields & required_fields),
            'completeness_percentage': (len(present_fields & required_fields) / len(required_fields)) * 100 if required_fields else 100
        }
        
        if not validation_result['is_complete']:
            logger.warning(
                f"Incomplete {response_type} response: missing {missing_fields}, empty {empty_fields}",
                extra={
                    'response_type': response_type,
                    'missing_fields': list(missing_fields),
                    'empty_fields': list(empty_fields),
                    'completeness_percentage': validation_result['completeness_percentage']
                }
            )
        
        return validation_result
    
    def validate_list_response(self, response_data: List[Dict[str, Any]], response_type: str) -> Dict[str, Any]:
        """
        Validar completitud de respuesta de lista
        
        Args:
            response_data: Lista de datos de respuesta
            response_type: Tipo de respuesta
            
        Returns:
            Resultado de validación agregado
        """
        if not response_data:
            return {
                'is_complete': True,
                'response_type': f'{response_type}_list',
                'total_items': 0,
                'complete_items': 0,
                'incomplete_items': 0,
                'completeness_percentage': 100.0,
                'validation_details': []
            }
        
        validation_details = []
        complete_items = 0
        
        for i, item in enumerate(response_data):
            item_validation = self._validate_response(item, response_type)
            item_validation['item_index'] = i
            validation_details.append(item_validation)
            
            if item_validation['is_complete']:
                complete_items += 1
        
        total_items = len(response_data)
        incomplete_items = total_items - complete_items
        
        return {
            'is_complete': incomplete_items == 0,
            'response_type': f'{response_type}_list',
            'total_items': total_items,
            'complete_items': complete_items,
            'incomplete_items': incomplete_items,
            'completeness_percentage': (complete_items / total_items) * 100 if total_items > 0 else 100.0,
            'validation_details': validation_details
        }
    
    def validate_pydantic_model_completeness(self, model_instance: BaseModel, response_type: str) -> Dict[str, Any]:
        """
        Validar completitud usando instancia de modelo Pydantic
        
        Args:
            model_instance: Instancia del modelo Pydantic
            response_type: Tipo de respuesta
            
        Returns:
            Resultado de validación
        """
        # Convertir modelo a diccionario
        response_data = model_instance.dict()
        return self._validate_response(response_data, response_type)
    
    def get_schema_validation_summary(self, response_type: str) -> Dict[str, Any]:
        """
        Obtener resumen de validación de esquema para un tipo de respuesta
        
        Args:
            response_type: Tipo de respuesta
            
        Returns:
            Resumen de campos requeridos y validaciones
        """
        required_fields = self.REQUIRED_FIELDS.get(response_type, set())
        
        return {
            'response_type': response_type,
            'required_fields': list(required_fields),
            'total_required_fields': len(required_fields),
            'validation_rules': {
                'no_missing_fields': 'All required fields must be present',
                'no_empty_values': 'Required fields cannot be None or empty strings',
                'type_validation': 'Fields must match expected data types'
            },
            'requirements_mapping': self._get_requirements_mapping(response_type)
        }
    
    def _get_requirements_mapping(self, response_type: str) -> Dict[str, str]:
        """
        Obtener mapeo de campos a requisitos específicos
        
        Args:
            response_type: Tipo de respuesta
            
        Returns:
            Mapeo de campos a requisitos
        """
        mappings = {
            'card': {
                'status': 'Requisito 3.4: estado de tarjeta',
                'card_type': 'Requisito 3.4: tipo de tarjeta',
                'expiry_month': 'Requisito 3.4: información de expiración',
                'expiry_year': 'Requisito 3.4: información de expiración',
                'masked_card_number': 'Requisito 3.2: enmascaramiento de información sensible'
            },
            'transaction': {
                'amount': 'Requisito 4.4: monto de transacción',
                'transaction_date': 'Requisito 4.4: fecha',
                'merchant_name': 'Requisito 4.4: comerciante',
                'status': 'Requisito 4.4: información de estado'
            },
            'account': {
                'account_number': 'Requisito 2.1: información completa de cuenta',
                'first_name': 'Requisito 2.1: detalles completos de cuenta',
                'last_name': 'Requisito 2.1: detalles completos de cuenta'
            }
        }
        
        return mappings.get(response_type, {})


# Instancia global del validador
_response_validator = None


def get_response_validator() -> ResponseCompletenessValidator:
    """
    Obtener instancia global del validador de completitud
    
    Returns:
        Instancia de ResponseCompletenessValidator
    """
    global _response_validator
    if _response_validator is None:
        _response_validator = ResponseCompletenessValidator()
    return _response_validator