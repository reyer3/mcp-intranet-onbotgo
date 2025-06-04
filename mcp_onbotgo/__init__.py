"""
MCP OnBotGo - Model Context Protocol Server for Task Management

Este paquete proporciona un servidor MCP completo para la gestión inteligente
de tareas del equipo OnBotGo, integrando APIs existentes con capacidades de IA.

Autor: Equipo OnBotGo
Versión: 1.0.0
Licencia: MIT
"""

__version__ = "1.0.0"
__author__ = "Equipo OnBotGo"
__email__ = "tech@onbotgo.com"
__description__ = "Model Context Protocol Server for OnBotGo Task Management"

# Importar clases principales para fácil acceso
try:
    from .server import MCPOnBotGoServer
    from .config import Config
except ImportError:
    # Durante la instalación, las dependencias pueden no estar disponibles
    pass

# Definir what's available when importing *
__all__ = [
    "MCPOnBotGoServer",
    "Config",
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]

# Configuración de logging básica
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())