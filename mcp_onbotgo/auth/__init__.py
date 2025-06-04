"""
Módulo de autenticación para MCP OnBotGo

Este módulo maneja toda la autenticación y autorización del sistema,
incluye integración con Google Identity Toolkit y gestión de permisos.
"""

from .google_auth import GoogleAuthManager
from .permissions import PermissionManager, Permission, Role

__all__ = [
    "GoogleAuthManager",
    "PermissionManager", 
    "Permission",
    "Role"
]