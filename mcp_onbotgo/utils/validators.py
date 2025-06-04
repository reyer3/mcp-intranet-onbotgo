"""
Validadores para MCP OnBotGo

Este módulo implementa validadores para diferentes tipos de datos
y entidades del sistema, asegurando integridad y consistencia.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from email.utils import parseaddr
import json

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Excepción personalizada para errores de validación"""
    def __init__(self, message: str, field: str = None, code: str = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(message)


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Valida formato de email
    
    Args:
        email: Email a validar
        
    Returns:
        Tuple (es_valido, mensaje_error)
    """
    if not email or not isinstance(email, str):
        return False, "Email requerido"
    
    # Usar parseaddr para validación básica
    parsed = parseaddr(email)
    if not parsed[1]:
        return False, "Formato de email inválido"
    
    # Validación adicional con regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Formato de email inválido"
    
    return True, None


def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, Optional[str]]:
    """
    Valida un rango de fechas
    
    Args:
        start_date: Fecha de inicio en formato ISO
        end_date: Fecha de fin en formato ISO
        
    Returns:
        Tuple (es_valido, mensaje_error)
    """
    try:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if start >= end:
            return False, "La fecha de inicio debe ser anterior a la fecha de fin"
        
        # Verificar que no sea un rango muy largo (más de 2 años)
        if (end - start).days > 730:
            return False, "El rango de fechas no puede ser mayor a 2 años"
        
        return True, None
        
    except ValueError as e:
        return False, f"Formato de fecha inválido: {str(e)}"


class TaskValidator:
    """Validador para entidades de tareas"""
    
    @staticmethod
    def validate_task_data(task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida datos de una tarea
        
        Args:
            task_data: Datos de la tarea a validar
            
        Returns:
            Dict con resultado de validación
        """
        errors = []
        warnings = []
        
        # Validar campos requeridos
        required_fields = ['name', 'projectuid']
        for field in required_fields:
            if not task_data.get(field):
                errors.append(f"Campo requerido: {field}")
        
        # Validar nombre de tarea
        name = task_data.get('name', '')
        if len(name) < 3:
            errors.append("El nombre de la tarea debe tener al menos 3 caracteres")
        elif len(name) > 200:
            errors.append("El nombre de la tarea no puede exceder 200 caracteres")
        
        # Validar descripción
        description = task_data.get('description', '')
        if len(description) > 5000:
            warnings.append("La descripción es muy larga (>5000 caracteres)")
        
        # Validar fecha de vencimiento
        expire_date = task_data.get('expire_date')
        if expire_date:
            try:
                due_date = datetime.fromisoformat(expire_date.replace('Z', '+00:00'))
                now = datetime.utcnow()
                
                if due_date < now:
                    warnings.append("La fecha de vencimiento está en el pasado")
                elif (due_date - now).days > 365:
                    warnings.append("La fecha de vencimiento está muy lejos (>1 año)")
                    
            except ValueError:
                errors.append("Formato de fecha de vencimiento inválido")
        
        # Validar usuarios asignados
        assigned_users = task_data.get('assigned_users', [])
        if assigned_users:
            if not isinstance(assigned_users, list):
                errors.append("assigned_users debe ser una lista")
            else:
                for i, user in enumerate(assigned_users):
                    if not isinstance(user, dict):
                        errors.append(f"Usuario asignado {i} debe ser un objeto")
                        continue
                    
                    if not user.get('uid'):
                        errors.append(f"Usuario asignado {i} requiere UID")
                    
                    if not user.get('email'):
                        errors.append(f"Usuario asignado {i} requiere email")
                    else:
                        valid_email, email_error = validate_email(user['email'])
                        if not valid_email:
                            errors.append(f"Email inválido en usuario {i}: {email_error}")
        
        # Validar etiquetas
        labels = task_data.get('labels', [])
        if labels and not isinstance(labels, list):
            errors.append("labels debe ser una lista")
        elif labels and not all(isinstance(label, int) for label in labels):
            errors.append("Todas las etiquetas deben ser números enteros")
        
        # Validar columna
        column_id = task_data.get('columnid')
        if column_id is not None and not isinstance(column_id, int):
            errors.append("columnid debe ser un número entero")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_task_update(update_data: Dict[str, Any], current_task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida actualización de tarea
        
        Args:
            update_data: Datos de actualización
            current_task: Estado actual de la tarea
            
        Returns:
            Dict con resultado de validación
        """
        errors = []
        warnings = []
        
        # Validar que no se estén modificando campos no permitidos
        readonly_fields = ['id', 'created_at', 'created_by']
        for field in readonly_fields:
            if field in update_data:
                errors.append(f"Campo de solo lectura: {field}")
        
        # Validar transiciones de estado
        new_status = update_data.get('status')
        current_status = current_task.get('status')
        
        if new_status and current_status:
            valid_transitions = {
                'pendiente': ['en_progreso', 'cancelada'],
                'en_progreso': ['completada', 'pendiente', 'bloqueada'],
                'completada': ['en_progreso'],  # Reabrir
                'cancelada': ['pendiente'],
                'bloqueada': ['en_progreso', 'pendiente']
            }
            
            allowed = valid_transitions.get(current_status, [])
            if new_status not in allowed:
                errors.append(f"Transición de estado inválida: {current_status} -> {new_status}")
        
        # Validar otros campos como en validate_task_data
        temp_task = current_task.copy()
        temp_task.update(update_data)
        
        validation_result = TaskValidator.validate_task_data(temp_task)
        errors.extend(validation_result['errors'])
        warnings.extend(validation_result['warnings'])
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


class ClientValidator:
    """Validador para entidades de clientes"""
    
    @staticmethod
    def validate_client_data(client_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida datos de un cliente
        
        Args:
            client_data: Datos del cliente a validar
            
        Returns:
            Dict con resultado de validación
        """
        errors = []
        warnings = []
        
        # Validar nombre
        name = client_data.get('name', '')
        if not name:
            errors.append("Nombre del cliente requerido")
        elif len(name) < 2:
            errors.append("El nombre del cliente debe tener al menos 2 caracteres")
        elif len(name) > 100:
            errors.append("El nombre del cliente no puede exceder 100 caracteres")
        
        # Validar email de contacto
        email = client_data.get('email')
        if email:
            valid_email, email_error = validate_email(email)
            if not valid_email:
                errors.append(f"Email del cliente inválido: {email_error}")
        
        # Validar país
        country = client_data.get('country')
        if country and len(country) > 50:
            warnings.append("El nombre del país es muy largo")
        
        # Validar estado
        active = client_data.get('active')
        if active is not None and not isinstance(active, bool):
            errors.append("El campo 'active' debe ser verdadero o falso")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_client_search_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida parámetros de búsqueda de clientes
        
        Args:
            params: Parámetros de búsqueda
            
        Returns:
            Dict con resultado de validación
        """
        errors = []
        warnings = []
        
        # Validar pageSize
        page_size = params.get('pageSize')
        if page_size is not None:
            if not isinstance(page_size, int) or page_size < 1:
                errors.append("pageSize debe ser un entero positivo")
            elif page_size > 100:
                warnings.append("pageSize muy grande (>100), puede afectar el rendimiento")
        
        # Validar offset
        offset = params.get('offset')
        if offset is not None and (not isinstance(offset, int) or offset < 0):
            errors.append("offset debe ser un entero no negativo")
        
        # Validar order
        order = params.get('order')
        if order and order not in ['ASC', 'DESC']:
            errors.append("order debe ser 'ASC' o 'DESC'")
        
        # Validar orderField
        order_field = params.get('orderField')
        valid_order_fields = ['name', 'created_at', 'updated_at', 'country']
        if order_field and order_field not in valid_order_fields:
            warnings.append(f"orderField '{order_field}' puede no estar soportado")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


class UserValidator:
    """Validador para entidades de usuarios"""
    
    @staticmethod
    def validate_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida datos de un usuario
        
        Args:
            user_data: Datos del usuario a validar
            
        Returns:
            Dict con resultado de validación
        """
        errors = []
        warnings = []
        
        # Validar UID
        uid = user_data.get('uid')
        if not uid:
            errors.append("UID del usuario requerido")
        elif not isinstance(uid, str) or len(uid) < 10:
            errors.append("UID del usuario inválido")
        
        # Validar email
        email = user_data.get('email')
        if not email:
            errors.append("Email del usuario requerido")
        else:
            valid_email, email_error = validate_email(email)
            if not valid_email:
                errors.append(f"Email del usuario inválido: {email_error}")
        
        # Validar displayName
        display_name = user_data.get('displayName', '')
        if len(display_name) > 100:
            warnings.append("Nombre de visualización muy largo")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_user_assignment(user_data: Dict[str, Any], task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida la asignación de un usuario a una tarea
        
        Args:
            user_data: Datos del usuario
            task_data: Datos de la tarea
            
        Returns:
            Dict con resultado de validación
        """
        errors = []
        warnings = []
        
        # Validar que el usuario sea válido
        user_validation = UserValidator.validate_user_data(user_data)
        if not user_validation['valid']:
            errors.extend(user_validation['errors'])
        
        # Validar que la tarea permita asignación
        task_status = task_data.get('status')
        if task_status in ['completada', 'cancelada']:
            errors.append("No se puede asignar usuario a tarea completada o cancelada")
        
        # Validar carga de trabajo (simulado)
        # En implementación real, consultarías la carga actual del usuario
        current_tasks = 5  # Mock
        if current_tasks > 10:
            warnings.append("El usuario tiene alta carga de trabajo")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


class MCPRequestValidator:
    """Validador para requests MCP"""
    
    @staticmethod
    def validate_tool_request(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida una request de herramienta MCP
        
        Args:
            tool_name: Nombre de la herramienta
            arguments: Argumentos de la herramienta
            
        Returns:
            Dict con resultado de validación
        """
        errors = []
        warnings = []
        
        # Definir esquemas de validación para cada herramienta
        tool_schemas = {
            "crear_tarea_inteligente": {
                "required": ["descripcion", "proyecto_id"],
                "optional": ["asignado_a", "fecha_vencimiento", "prioridad"]
            },
            "buscar_tareas_semantica": {
                "required": ["query"],
                "optional": ["proyecto_id", "estado", "asignado_a", "incluir_contexto_cliente", "limite"]
            },
            "actualizar_tarea_contextual": {
                "required": ["tarea_id", "cambios"],
                "optional": ["comentario_automatico", "notificar_asignado"]
            },
            "buscar_cliente_inteligente": {
                "required": ["query"],
                "optional": ["activos_solo", "incluir_proyectos"]
            }
        }
        
        schema = tool_schemas.get(tool_name)
        if not schema:
            warnings.append(f"Esquema de validación no disponible para herramienta: {tool_name}")
            return {
                "valid": True,
                "errors": errors,
                "warnings": warnings
            }
        
        # Validar campos requeridos
        for field in schema["required"]:
            if field not in arguments:
                errors.append(f"Campo requerido faltante: {field}")
            elif not arguments[field]:  # Verificar que no esté vacío
                errors.append(f"Campo requerido vacío: {field}")
        
        # Validar tipos de datos específicos
        if tool_name == "crear_tarea_inteligente":
            descripcion = arguments.get("descripcion", "")
            if len(descripcion) < 10:
                warnings.append("Descripción muy corta para análisis efectivo")
            elif len(descripcion) > 2000:
                warnings.append("Descripción muy larga, puede afectar el rendimiento")
        
        elif tool_name == "actualizar_tarea_contextual":
            tarea_id = arguments.get("tarea_id")
            if tarea_id is not None and not isinstance(tarea_id, int):
                errors.append("tarea_id debe ser un número entero")
            
            cambios = arguments.get("cambios", {})
            if not isinstance(cambios, dict):
                errors.append("cambios debe ser un objeto")
            elif not cambios:
                warnings.append("No se especificaron cambios a realizar")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    @staticmethod
    def sanitize_arguments(arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza argumentos de entrada
        
        Args:
            arguments: Argumentos a sanitizar
            
        Returns:
            Dict con argumentos sanitizados
        """
        sanitized = {}
        
        for key, value in arguments.items():
            if isinstance(value, str):
                # Limpiar strings
                value = value.strip()
                # Remover caracteres potencialmente peligrosos
                value = re.sub(r'[<>"\']', '', value)
            elif isinstance(value, dict):
                # Sanitizar recursivamente
                value = MCPRequestValidator.sanitize_arguments(value)
            elif isinstance(value, list):
                # Sanitizar elementos de lista
                value = [MCPRequestValidator.sanitize_arguments({"item": item})["item"] 
                        if isinstance(item, (dict, list)) else item for item in value]
            
            sanitized[key] = value
        
        return sanitized