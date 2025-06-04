"""
Configuración del sistema MCP OnBotGo

Este módulo maneja toda la configuración del servidor MCP,
incluye validación de variables de entorno y configuración por defecto.
"""

import os
from typing import Optional, List, Union
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Configuración principal del sistema MCP OnBotGo"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"  # Permitir campos adicionales
    )
    
    # Configuración MCP Server
    mcp_server_name: str = Field(
        default="OnBotGo Task Manager", 
        description="Nombre del servidor MCP"
    )
    mcp_server_version: str = Field(
        default="1.0.0", 
        description="Versión del servidor"
    )
    mcp_host: str = Field(
        default="localhost", 
        description="Host del servidor MCP"
    )
    mcp_port: int = Field(
        default=8000, 
        description="Puerto del servidor MCP"
    )
    
    # Google Identity Toolkit
    google_api_key: str = Field(
        default="AIzaSyAXtP5xZXh3glObbvk6FHMbfe1o0_9dVwY", 
        description="API Key de Google Identity Toolkit"
    )
    google_client_id: str = Field(
        default="tu_client_id.apps.googleusercontent.com", 
        description="Client ID de Google OAuth"
    )
    google_client_secret: str = Field(
        default="tu_client_secret", 
        description="Client Secret de Google OAuth"
    )
    google_redirect_uri: str = Field(
        default="http://localhost:8000/oauth/callback", 
        description="URI de redirección OAuth"
    )
    
    # APIs OnBotGo
    apiaim_base_url: str = Field(
        default="https://apiaim.mibot.cl", 
        description="URL base de la API Apiaim"
    )
    intranet_base_url: str = Field(
        default="https://apiintranet.mibot.cl", 
        description="URL base de la API Intranet"
    )
    default_mibot_session: str = Field(
        default='{"project_uid":"vnbLnzdM0b3BDClTPVPL","client_uid":"lEvxdkHyFXdOX4ieEMHs"}',
        description="Sesión por defecto para APIs Mibot"
    )
    
    # Base de datos
    database_url: str = Field(
        default="sqlite:///./mcp_onbotgo.db", 
        description="URL de conexión a la base de datos"
    )
    
    # Redis/Cache
    redis_url: str = Field(
        default="redis://localhost:6379/0", 
        description="URL de conexión a Redis"
    )
    redis_password: Optional[str] = Field(
        default=None, 
        description="Contraseña de Redis"
    )
    redis_db: int = Field(
        default=0, 
        description="Base de datos Redis"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO", 
        description="Nivel de logging"
    )
    log_format: str = Field(
        default="json", 
        description="Formato de logs"
    )
    log_file: str = Field(
        default="logs/mcp_onbotgo.log", 
        description="Archivo de logs"
    )
    
    # AI Configuration
    openai_api_key: Optional[str] = Field(
        default=None, 
        description="API Key de OpenAI"
    )
    openai_model: str = Field(
        default="gpt-4o-mini", 
        description="Modelo de OpenAI a usar"
    )
    max_tokens: int = Field(
        default=4000, 
        description="Máximo tokens para respuestas AI"
    )
    
    # Security
    secret_key: str = Field(
        default="tu_secret_key_muy_segura_de_32_caracteres_minimo", 
        description="Clave secreta para JWT"
    )
    algorithm: str = Field(
        default="HS256", 
        description="Algoritmo para JWT"
    )
    access_token_expire_minutes: int = Field(
        default=30, 
        description="Minutos de expiración del token de acceso"
    )
    refresh_token_expire_days: int = Field(
        default=7, 
        description="Días de expiración del token de refresh"
    )
    
    # Feature Flags
    enable_ai_analysis: bool = Field(
        default=True, 
        description="Habilitar análisis con IA"
    )
    enable_real_time_notifications: bool = Field(
        default=True, 
        description="Habilitar notificaciones en tiempo real"
    )
    enable_automatic_assignment: bool = Field(
        default=True, 
        description="Habilitar asignación automática"
    )
    enable_client_auto_detection: bool = Field(
        default=True, 
        description="Habilitar detección automática de clientes"
    )
    enable_performance_metrics: bool = Field(
        default=True, 
        description="Habilitar métricas de rendimiento"
    )
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=60, 
        description="Límite de requests por minuto"
    )
    rate_limit_per_hour: int = Field(
        default=1000, 
        description="Límite de requests por hora"
    )
    
    # Development
    debug: bool = Field(
        default=False, 
        description="Modo debug"
    )
    testing: bool = Field(
        default=False, 
        description="Modo testing"
    )
    development: bool = Field(
        default=False, 
        description="Modo desarrollo"
    )
    
    # CORS
    cors_origins: Union[List[str], str] = Field(
        default="http://localhost:3000",
        description="Orígenes permitidos para CORS"
    )
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        """Parsear CORS origins desde string separado por comas"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validar nivel de logging"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()
    
    @property
    def is_production(self) -> bool:
        """Verificar si estamos en producción"""
        return not (self.debug or self.testing or self.development)
    
    @property
    def database_echo(self) -> bool:
        """Determinar si SQLAlchemy debe hacer echo de queries"""
        return self.debug and not self.testing
    
    def get_mibot_session_dict(self) -> dict:
        """Obtener sesión Mibot como diccionario"""
        import json
        try:
            return json.loads(self.default_mibot_session)
        except json.JSONDecodeError:
            return {"project_uid": "default", "client_uid": "default"}


# Instancia global de configuración
config = None


def get_config() -> Config:
    """Obtener la configuración global"""
    global config
    if config is None:
        config = Config()
    return config


def reload_config() -> Config:
    """Recargar la configuración desde variables de entorno"""
    global config
    config = Config()
    return config