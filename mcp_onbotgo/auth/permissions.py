"""
Sistema de permisos y roles para MCP OnBotGo

Este módulo implementa un sistema granular de permisos basado en roles
para controlar el acceso a las funcionalidades del sistema.
"""

import logging
from enum import Enum
from typing import List, Set, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


class Permission(Enum):
    """Enumeración de permisos disponibles en el sistema"""
    
    # Permisos de lectura
    READ_TASKS = "read_tasks"
    READ_CLIENTS = "read_clients"
    READ_PROJECTS = "read_projects"
    READ_USERS = "read_users"
    READ_ANALYTICS = "read_analytics"
    READ_COMMENTS = "read_comments"
    
    # Permisos de escritura
    CREATE_TASKS = "create_tasks"
    UPDATE_TASKS = "update_tasks"
    DELETE_TASKS = "delete_tasks"
    ASSIGN_TASKS = "assign_tasks"
    
    # Permisos de clientes
    CREATE_CLIENTS = "create_clients"
    UPDATE_CLIENTS = "update_clients"
    DELETE_CLIENTS = "delete_clients"
    
    # Permisos de proyectos
    CREATE_PROJECTS = "create_projects"
    UPDATE_PROJECTS = "update_projects"
    DELETE_PROJECTS = "delete_projects"
    MANAGE_PROJECT_MEMBERS = "manage_project_members"
    
    # Permisos de comentarios
    CREATE_COMMENTS = "create_comments"
    UPDATE_COMMENTS = "update_comments"
    DELETE_COMMENTS = "delete_comments"
    MODERATE_COMMENTS = "moderate_comments"
    
    # Permisos administrativos
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    VIEW_SYSTEM_LOGS = "view_system_logs"
    MANAGE_SYSTEM_CONFIG = "manage_system_config"
    
    # Permisos avanzados
    USE_AI_FEATURES = "use_ai_features"
    ACCESS_ANALYTICS = "access_analytics"
    EXPORT_DATA = "export_data"
    IMPORT_DATA = "import_data"
    
    # Permisos especiales
    IMPERSONATE_USER = "impersonate_user"
    BYPASS_RATE_LIMITS = "bypass_rate_limits"
    ACCESS_DEBUG_INFO = "access_debug_info"


class Role(Enum):
    """Enumeración de roles disponibles en el sistema"""
    
    # Roles básicos
    GUEST = "guest"
    USER = "user"
    MEMBER = "member"
    
    # Roles especializados
    DEVELOPER = "developer"
    DESIGNER = "designer"
    QA_TESTER = "qa_tester"
    
    # Roles de gestión
    PROJECT_MANAGER = "project_manager"
    TEAM_LEAD = "team_lead"
    ACCOUNT_MANAGER = "account_manager"
    
    # Roles administrativos
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    SYSTEM_ADMIN = "system_admin"


@dataclass
class UserPermissions:
    """Clase para almacenar permisos de un usuario"""
    user_id: str
    email: str
    roles: Set[Role]
    permissions: Set[Permission]
    granted_at: datetime
    expires_at: Optional[datetime] = None
    granted_by: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class PermissionManager:
    """Gestor del sistema de permisos y roles"""
    
    def __init__(self, config):
        self.config = config
        self._role_permissions = self._initialize_role_permissions()
        self._user_permissions_cache: Dict[str, UserPermissions] = {}
        
        logger.info("PermissionManager inicializado")
    
    def _initialize_role_permissions(self) -> Dict[Role, Set[Permission]]:
        """Inicializa la matriz de permisos por rol"""
        role_permissions = {
            # Guest - Solo lectura limitada
            Role.GUEST: {
                Permission.READ_TASKS,
                Permission.READ_PROJECTS
            },
            
            # User - Operaciones básicas
            Role.USER: {
                Permission.READ_TASKS,
                Permission.READ_CLIENTS,
                Permission.READ_PROJECTS,
                Permission.READ_COMMENTS,
                Permission.CREATE_TASKS,
                Permission.UPDATE_TASKS,
                Permission.CREATE_COMMENTS,
                Permission.UPDATE_COMMENTS,
                Permission.USE_AI_FEATURES
            },
            
            # Member - Usuario con más capacidades
            Role.MEMBER: {
                Permission.READ_TASKS,
                Permission.READ_CLIENTS,
                Permission.READ_PROJECTS,
                Permission.READ_COMMENTS,
                Permission.READ_ANALYTICS,
                Permission.CREATE_TASKS,
                Permission.UPDATE_TASKS,
                Permission.ASSIGN_TASKS,
                Permission.CREATE_COMMENTS,
                Permission.UPDATE_COMMENTS,
                Permission.DELETE_COMMENTS,
                Permission.USE_AI_FEATURES,
                Permission.ACCESS_ANALYTICS,
                Permission.EXPORT_DATA
            },
            
            # Developer - Permisos técnicos
            Role.DEVELOPER: {
                Permission.READ_TASKS,
                Permission.READ_CLIENTS,
                Permission.READ_PROJECTS,
                Permission.READ_COMMENTS,
                Permission.READ_ANALYTICS,
                Permission.CREATE_TASKS,
                Permission.UPDATE_TASKS,
                Permission.DELETE_TASKS,
                Permission.ASSIGN_TASKS,
                Permission.CREATE_COMMENTS,
                Permission.UPDATE_COMMENTS,
                Permission.DELETE_COMMENTS,
                Permission.USE_AI_FEATURES,
                Permission.ACCESS_ANALYTICS,
                Permission.EXPORT_DATA,
                Permission.IMPORT_DATA,
                Permission.ACCESS_DEBUG_INFO
            },
            
            # Project Manager - Gestión de proyectos
            Role.PROJECT_MANAGER: {
                Permission.READ_TASKS,
                Permission.READ_CLIENTS,
                Permission.READ_PROJECTS,
                Permission.READ_USERS,
                Permission.READ_ANALYTICS,
                Permission.READ_COMMENTS,
                Permission.CREATE_TASKS,
                Permission.UPDATE_TASKS,
                Permission.DELETE_TASKS,
                Permission.ASSIGN_TASKS,
                Permission.CREATE_PROJECTS,
                Permission.UPDATE_PROJECTS,
                Permission.MANAGE_PROJECT_MEMBERS,
                Permission.CREATE_COMMENTS,
                Permission.UPDATE_COMMENTS,
                Permission.DELETE_COMMENTS,
                Permission.MODERATE_COMMENTS,
                Permission.USE_AI_FEATURES,
                Permission.ACCESS_ANALYTICS,
                Permission.EXPORT_DATA,
                Permission.IMPORT_DATA
            },
            
            # Team Lead - Liderazgo de equipo
            Role.TEAM_LEAD: {
                Permission.READ_TASKS,
                Permission.READ_CLIENTS,
                Permission.READ_PROJECTS,
                Permission.READ_USERS,
                Permission.READ_ANALYTICS,
                Permission.READ_COMMENTS,
                Permission.CREATE_TASKS,
                Permission.UPDATE_TASKS,
                Permission.DELETE_TASKS,
                Permission.ASSIGN_TASKS,
                Permission.UPDATE_PROJECTS,
                Permission.MANAGE_PROJECT_MEMBERS,
                Permission.CREATE_COMMENTS,
                Permission.UPDATE_COMMENTS,
                Permission.DELETE_COMMENTS,
                Permission.MODERATE_COMMENTS,
                Permission.USE_AI_FEATURES,
                Permission.ACCESS_ANALYTICS,
                Permission.EXPORT_DATA,
                Permission.MANAGE_USERS
            },
            
            # Admin - Administración completa
            Role.ADMIN: set(Permission),  # Todos los permisos excepto los de super admin
            
            # Super Admin - Permisos absolutos
            Role.SUPER_ADMIN: set(Permission)  # Todos los permisos
        }
        
        # Eliminar permisos especiales del admin regular
        if Role.ADMIN in role_permissions:
            role_permissions[Role.ADMIN] -= {
                Permission.IMPERSONATE_USER,
                Permission.MANAGE_SYSTEM_CONFIG,
                Permission.VIEW_SYSTEM_LOGS
            }
        
        return role_permissions
    
    def get_permissions_for_role(self, role: Role) -> Set[Permission]:
        """Obtiene todos los permisos para un rol específico"""
        return self._role_permissions.get(role, set())
    
    def get_permissions_for_roles(self, roles: List[Role]) -> Set[Permission]:
        """Obtiene todos los permisos para una lista de roles"""
        permissions = set()
        for role in roles:
            permissions.update(self.get_permissions_for_role(role))
        return permissions
    
    def has_permission(self, user_permissions: UserPermissions, permission: Permission) -> bool:
        """Verifica si un usuario tiene un permiso específico"""
        # Verificar si el permiso está expirado
        if user_permissions.expires_at and user_permissions.expires_at < datetime.utcnow():
            logger.warning(f"Permisos expirados para usuario {user_permissions.user_id}")
            return False
        
        # Verificar permiso directo
        if permission in user_permissions.permissions:
            return True
        
        # Verificar permisos por rol
        role_permissions = self.get_permissions_for_roles(list(user_permissions.roles))
        return permission in role_permissions
    
    def has_any_permission(self, user_permissions: UserPermissions, permissions: List[Permission]) -> bool:
        """Verifica si un usuario tiene al menos uno de los permisos especificados"""
        return any(self.has_permission(user_permissions, perm) for perm in permissions)
    
    def has_all_permissions(self, user_permissions: UserPermissions, permissions: List[Permission]) -> bool:
        """Verifica si un usuario tiene todos los permisos especificados"""
        return all(self.has_permission(user_permissions, perm) for perm in permissions)
    
    def get_user_permissions(self, user_id: str, email: str, roles: List[str]) -> UserPermissions:
        """Obtiene los permisos completos de un usuario"""
        # Convertir strings a enums de roles
        user_roles = set()
        for role_str in roles:
            try:
                role = Role(role_str.lower())
                user_roles.add(role)
            except ValueError:
                logger.warning(f"Rol desconocido: {role_str}")
        
        # Si no hay roles válidos, asignar rol básico
        if not user_roles:
            user_roles.add(Role.USER)
        
        # Obtener permisos combinados de todos los roles
        combined_permissions = self.get_permissions_for_roles(list(user_roles))
        
        user_permissions = UserPermissions(
            user_id=user_id,
            email=email,
            roles=user_roles,
            permissions=combined_permissions,
            granted_at=datetime.utcnow()
        )
        
        # Cachear permisos
        self._user_permissions_cache[user_id] = user_permissions
        
        return user_permissions
    
    def get_cached_user_permissions(self, user_id: str) -> Optional[UserPermissions]:
        """Obtiene permisos de usuario desde el cache"""
        return self._user_permissions_cache.get(user_id)
    
    def clear_user_permissions_cache(self, user_id: str = None):
        """Limpia el cache de permisos de usuario"""
        if user_id:
            self._user_permissions_cache.pop(user_id, None)
        else:
            self._user_permissions_cache.clear()
    
    def add_temporary_permission(self, user_id: str, permission: Permission, duration_minutes: int = 60):
        """Agrega un permiso temporal a un usuario"""
        user_permissions = self._user_permissions_cache.get(user_id)
        if user_permissions:
            user_permissions.permissions.add(permission)
            user_permissions.expires_at = datetime.utcnow() + timedelta(minutes=duration_minutes)
            logger.info(f"Permiso temporal {permission} agregado a usuario {user_id} por {duration_minutes} minutos")
    
    def remove_permission(self, user_id: str, permission: Permission):
        """Remueve un permiso específico de un usuario"""
        user_permissions = self._user_permissions_cache.get(user_id)
        if user_permissions and permission in user_permissions.permissions:
            user_permissions.permissions.remove(permission)
            logger.info(f"Permiso {permission} removido del usuario {user_id}")
    
    def get_role_hierarchy(self) -> Dict[Role, int]:
        """Obtiene la jerarquía de roles (mayor número = más permisos)"""
        return {
            Role.GUEST: 0,
            Role.USER: 1,
            Role.MEMBER: 2,
            Role.DEVELOPER: 3,
            Role.DESIGNER: 3,
            Role.QA_TESTER: 3,
            Role.PROJECT_MANAGER: 4,
            Role.TEAM_LEAD: 5,
            Role.ACCOUNT_MANAGER: 4,
            Role.ADMIN: 8,
            Role.SUPER_ADMIN: 10,
            Role.SYSTEM_ADMIN: 9
        }
    
    def can_assign_role(self, assigner_roles: List[Role], target_role: Role) -> bool:
        """Verifica si un usuario puede asignar un rol específico"""
        hierarchy = self.get_role_hierarchy()
        
        # Obtener el nivel más alto del asignador
        max_assigner_level = max([hierarchy.get(role, 0) for role in assigner_roles])
        target_level = hierarchy.get(target_role, 0)
        
        # Solo puede asignar roles de nivel inferior o igual
        return max_assigner_level >= target_level
    
    def validate_mcp_context(self, user_permissions: UserPermissions, tool_name: str) -> bool:
        """Valida permisos específicos para herramientas MCP"""
        # Mapeo de herramientas MCP a permisos requeridos
        tool_permissions = {
            "crear_tarea_inteligente": [Permission.CREATE_TASKS, Permission.USE_AI_FEATURES],
            "buscar_tareas_semantica": [Permission.READ_TASKS, Permission.USE_AI_FEATURES],
            "actualizar_tarea_contextual": [Permission.UPDATE_TASKS],
            "buscar_cliente_inteligente": [Permission.READ_CLIENTS],
            "obtener_historial_cliente": [Permission.READ_CLIENTS, Permission.READ_ANALYTICS],
            "analizar_productividad_equipo": [Permission.ACCESS_ANALYTICS],
            "detectar_cuellos_botella": [Permission.ACCESS_ANALYTICS],
            "generar_reporte_proyecto": [Permission.READ_PROJECTS, Permission.ACCESS_ANALYTICS],
            "gestionar_usuarios": [Permission.MANAGE_USERS],
            "exportar_datos": [Permission.EXPORT_DATA]
        }
        
        required_permissions = tool_permissions.get(tool_name, [])
        
        if not required_permissions:
            # Si no se especifican permisos, permitir acceso básico
            return True
        
        # Verificar que tenga al menos uno de los permisos requeridos
        return self.has_any_permission(user_permissions, required_permissions)