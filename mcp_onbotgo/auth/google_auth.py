"""
Gestión de autenticación con Google Identity Toolkit

Este módulo implementa la integración completa con Google Identity Toolkit
para autenticación OAuth 2.1 y gestión de tokens JWT.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import httpx
import json

logger = logging.getLogger(__name__)


class GoogleAuthManager:
    """Gestor de autenticación con Google Identity Toolkit"""
    
    def __init__(self, config):
        self.config = config
        self.base_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty"
        self.token_url = "https://securetoken.googleapis.com/v1/token"
        self.client = httpx.AsyncClient()
        
        logger.info("GoogleAuthManager inicializado")
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Autentica un usuario usando email y contraseña
        
        Args:
            email: Email del usuario
            password: Contraseña del usuario
            
        Returns:
            Dict con información del usuario autenticado y tokens
        """
        try:
            # Llamar a la API de Google Identity Toolkit
            auth_data = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            url = f"{self.base_url}/verifyPassword"
            params = {"key": self.config.google_api_key}
            
            response = await self.client.post(url, params=params, json=auth_data)
            
            if response.status_code == 200:
                result = response.json()
                
                # Procesar respuesta exitosa
                user_info = {
                    "user_id": result.get("localId"),
                    "email": result.get("email"),
                    "display_name": result.get("displayName", ""),
                    "id_token": result.get("idToken"),
                    "refresh_token": result.get("refreshToken"),
                    "expires_in": int(result.get("expiresIn", 3600)),
                    "registered": result.get("registered", True)
                }
                
                logger.info(f"Usuario autenticado exitosamente: {email}")
                return {
                    "success": True,
                    "user": user_info,
                    "message": "Autenticación exitosa"
                }
            else:
                error_info = response.json()
                logger.warning(f"Error de autenticación para {email}: {error_info}")
                return {
                    "success": False,
                    "error": error_info.get("error", {}).get("message", "Error de autenticación"),
                    "code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error en authenticate_user: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error interno: {str(e)}",
                "code": 500
            }
    
    async def get_user_info(self, id_token: str) -> Dict[str, Any]:
        """
        Obtiene información detallada del usuario usando su ID token
        
        Args:
            id_token: Token JWT de identificación
            
        Returns:
            Dict con información detallada del usuario
        """
        try:
            url = f"{self.base_url}/getAccountInfo"
            params = {"key": self.config.google_api_key}
            data = {"idToken": id_token}
            
            response = await self.client.post(url, params=params, json=data)
            
            if response.status_code == 200:
                result = response.json()
                users = result.get("users", [])
                
                if users:
                    user = users[0]
                    return {
                        "success": True,
                        "user": {
                            "user_id": user.get("localId"),
                            "email": user.get("email"),
                            "email_verified": user.get("emailVerified", False),
                            "display_name": user.get("displayName", ""),
                            "photo_url": user.get("photoUrl", ""),
                            "created_at": user.get("createdAt"),
                            "last_login_at": user.get("lastLoginAt"),
                            "provider_data": user.get("providerUserInfo", [])
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": "Usuario no encontrado"
                    }
            else:
                error_info = response.json()
                return {
                    "success": False,
                    "error": error_info.get("error", {}).get("message", "Error obteniendo información del usuario")
                }
                
        except Exception as e:
            logger.error(f"Error en get_user_info: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error interno: {str(e)}"
            }
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Renueva el token de acceso usando el refresh token
        
        Args:
            refresh_token: Token de renovación
            
        Returns:
            Dict con nuevos tokens
        """
        try:
            url = self.token_url
            params = {"key": self.config.google_api_key}
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
            
            # Usar form data para este endpoint
            response = await self.client.post(
                url, 
                params=params, 
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "tokens": {
                        "access_token": result.get("access_token"),
                        "id_token": result.get("id_token"),
                        "refresh_token": result.get("refresh_token"),
                        "expires_in": int(result.get("expires_in", 3600)),
                        "token_type": result.get("token_type", "Bearer"),
                        "user_id": result.get("user_id"),
                        "project_id": result.get("project_id")
                    }
                }
            else:
                error_info = response.json()
                return {
                    "success": False,
                    "error": error_info.get("error", {}).get("message", "Error renovando token")
                }
                
        except Exception as e:
            logger.error(f"Error en refresh_token: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error interno: {str(e)}"
            }
    
    def validate_jwt_token(self, token: str) -> Dict[str, Any]:
        """
        Valida un token JWT localmente
        
        Args:
            token: Token JWT a validar
            
        Returns:
            Dict con resultado de validación y payload del token
        """
        try:
            # Decodificar sin verificar la firma (para desarrollo)
            # En producción, verificar con la clave pública de Google
            payload = jwt.decode(token, options={"verify_signature": False})
            
            # Verificar expiración
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                return {
                    "valid": False,
                    "error": "Token expirado",
                    "payload": payload
                }
            
            return {
                "valid": True,
                "payload": payload,
                "user_id": payload.get("user_id", payload.get("sub")),
                "email": payload.get("email"),
                "expires_at": datetime.fromtimestamp(exp) if exp else None
            }
            
        except jwt.DecodeError:
            return {
                "valid": False,
                "error": "Token inválido"
            }
        except Exception as e:
            logger.error(f"Error validando JWT: {e}")
            return {
                "valid": False,
                "error": f"Error de validación: {str(e)}"
            }
    
    def create_session_token(self, user_info: Dict[str, Any]) -> str:
        """
        Crea un token de sesión personalizado para MCP
        
        Args:
            user_info: Información del usuario autenticado
            
        Returns:
            Token JWT de sesión
        """
        try:
            # Crear payload para el token de sesión
            now = datetime.utcnow()
            payload = {
                "user_id": user_info.get("user_id"),
                "email": user_info.get("email"),
                "display_name": user_info.get("display_name", ""),
                "iat": now,
                "exp": now + timedelta(minutes=self.config.access_token_expire_minutes),
                "iss": "mcp-onbotgo",
                "aud": "onbotgo-team"
            }
            
            # Crear token JWT
            token = jwt.encode(
                payload,
                self.config.secret_key,
                algorithm=self.config.algorithm
            )
            
            logger.info(f"Token de sesión creado para usuario: {user_info.get('email')}")
            return token
            
        except Exception as e:
            logger.error(f"Error creando token de sesión: {e}")
            raise
    
    async def validate_session_token(self, token: str) -> Dict[str, Any]:
        """
        Valida un token de sesión MCP
        
        Args:
            token: Token de sesión a validar
            
        Returns:
            Dict con resultado de validación
        """
        try:
            payload = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=[self.config.algorithm]
            )
            
            # Verificar que el token no haya expirado
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                return {
                    "valid": False,
                    "error": "Token de sesión expirado"
                }
            
            return {
                "valid": True,
                "user_id": payload.get("user_id"),
                "email": payload.get("email"),
                "display_name": payload.get("display_name"),
                "payload": payload
            }
            
        except jwt.ExpiredSignatureError:
            return {
                "valid": False,
                "error": "Token de sesión expirado"
            }
        except jwt.InvalidTokenError:
            return {
                "valid": False,
                "error": "Token de sesión inválido"
            }
        except Exception as e:
            logger.error(f"Error validando token de sesión: {e}")
            return {
                "valid": False,
                "error": f"Error de validación: {str(e)}"
            }
    
    async def close(self):
        """Cerrar cliente HTTP"""
        await self.client.aclose()
    
    def __del__(self):
        """Destructor para limpiar recursos"""
        try:
            # Intentar cerrar el cliente si aún está activo
            if hasattr(self, 'client') and self.client:
                asyncio.create_task(self.client.aclose())
        except Exception:
            pass  # Ignorar errores durante la limpieza