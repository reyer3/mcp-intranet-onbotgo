"""
Módulo de integraciones para MCP OnBotGo

Este módulo contiene clientes para integrarse con las APIs existentes
de OnBotGo (Apiaim e Intranet) y otros servicios externos.
"""

from .apiaim_client import ApiaimClient
from .intranet_client import IntranetClient

__all__ = [
    "ApiaimClient",
    "IntranetClient"
]