"""
Cliente para API Apiaim de OnBotGo

Este módulo implementa el cliente para interactuar con la API Apiaim,
incluye todas las operaciones de búsqueda de clientes y gestión de usuarios.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import httpx
import json

logger = logging.getLogger(__name__)


class ApiaimClient:
    """Cliente para interactuar con la API Apiaim"""
    
    def __init__(self, config):
        self.config = config
        self.base_url = config.apiaim_base_url
        self.default_session = config.get_mibot_session_dict()
        
        # Configurar cliente HTTP
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "MCP-OnBotGo/1.0"
            }
        )
        
        logger.info(f"ApiaimClient inicializado - Base URL: {self.base_url}")
    
    def _get_session_header(self, session_override: Optional[Dict[str, str]] = None) -> str:
        """Obtiene el header de sesión para las requests"""
        session_data = session_override or self.default_session
        return json.dumps(session_data)
    
    async def buscar_clientes(
        self,
        search: str = "",
        active: bool = True,
        pageSize: int = 20,
        offset: int = 0,
        order: str = "ASC",
        orderField: str = "name",
        filters: Optional[Dict[str, Any]] = None,
        session: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Busca clientes en el sistema Apiaim
        
        Args:
            search: Término de búsqueda
            active: Filtrar por clientes activos
            pageSize: Tamaño de página
            offset: Desplazamiento para paginación
            order: Orden (ASC/DESC)
            orderField: Campo para ordenar
            filters: Filtros adicionales
            session: Sesión personalizada
            
        Returns:
            Dict con resultado de la búsqueda
        """
        try:
            logger.info(f"Buscando clientes: search='{search}', active={active}")
            
            # Preparar parámetros de consulta
            params = {
                "active": active,
                "search": search,
                "pageSize": pageSize,
                "offset": offset,
                "order": order,
                "orderField": orderField
            }
            
            # Preparar cuerpo de la request
            body = {
                "filters": filters or {"type": [], "stage": []}
            }
            
            # Preparar headers con sesión
            headers = {
                "mibot_session": self._get_session_header(session)
            }
            
            # Realizar request
            response = await self.client.post(
                f"{self.base_url}/v3/clients/search",
                params=params,
                json=body,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Búsqueda exitosa: {len(result.get('data', []))} clientes encontrados")
                return result
            else:
                logger.error(f"Error en búsqueda de clientes: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "data": [],
                    "dataLength": 0
                }
                
        except Exception as e:
            logger.error(f"Error en buscar_clientes: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error interno: {str(e)}",
                "data": [],
                "dataLength": 0
            }
    
    async def obtener_cliente_por_id(
        self,
        client_id: str,
        session: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Obtiene un cliente específico por su ID
        
        Args:
            client_id: UID del cliente
            session: Sesión personalizada
            
        Returns:
            Dict con información del cliente
        """
        try:
            logger.info(f"Obteniendo cliente por ID: {client_id}")
            
            # Preparar headers
            headers = {
                "mibot_session": self._get_session_header(session)
            }
            
            # Realizar request
            response = await self.client.get(
                f"{self.base_url}/v3/clients/{client_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Cliente obtenido exitosamente: {client_id}")
                return result
            elif response.status_code == 404:
                logger.warning(f"Cliente no encontrado: {client_id}")
                return {
                    "success": False,
                    "error": "Cliente no encontrado",
                    "data": None
                }
            else:
                logger.error(f"Error obteniendo cliente {client_id}: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Error en obtener_cliente_por_id: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error interno: {str(e)}",
                "data": None
            }
    
    async def obtener_usuario_con_clientes(
        self,
        user_id: str,
        session: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Obtiene un usuario con todos sus clientes asociados
        
        Args:
            user_id: UID del usuario
            session: Sesión personalizada
            
        Returns:
            Dict con información del usuario y sus clientes
        """
        try:
            logger.info(f"Obteniendo usuario con clientes: {user_id}")
            
            # Preparar headers
            headers = {
                "mibot_session": self._get_session_header(session)
            }
            
            # Realizar request
            response = await self.client.get(
                f"{self.base_url}/v3/users/withAllClients/{user_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Usuario con clientes obtenido: {user_id}")
                return result
            else:
                logger.error(f"Error obteniendo usuario {user_id}: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Error en obtener_usuario_con_clientes: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error interno: {str(e)}",
                "data": None
            }
    
    async def obtener_menus_navegacion(
        self,
        actives: bool = True,
        session: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Obtiene los menús de navegación disponibles
        
        Args:
            actives: Solo menús activos
            session: Sesión personalizada
            
        Returns:
            Dict con estructura de menús
        """
        try:
            logger.info(f"Obteniendo menús de navegación: actives={actives}")
            
            # Preparar parámetros
            params = {"actives": actives}
            
            # Preparar headers
            headers = {
                "mibot_session": self._get_session_header(session)
            }
            
            # Realizar request
            response = await self.client.get(
                f"{self.base_url}/v3/menus_navigation",
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("Menús de navegación obtenidos exitosamente")
                return result
            else:
                logger.error(f"Error obteniendo menús: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "data": []
                }
                
        except Exception as e:
            logger.error(f"Error en obtener_menus_navegacion: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error interno: {str(e)}",
                "data": []
            }
    
    async def buscar_clientes_por_termino(
        self,
        termino: str,
        limite: int = 10,
        session: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda simplificada de clientes por término
        
        Args:
            termino: Término de búsqueda
            limite: Límite de resultados
            session: Sesión personalizada
            
        Returns:
            Lista de clientes encontrados
        """
        resultado = await self.buscar_clientes(
            search=termino,
            active=True,
            pageSize=limite,
            session=session
        )
        
        if resultado.get("success"):
            return resultado.get("data", [])
        else:
            logger.warning(f"Búsqueda fallida para término: {termino}")
            return []
    
    async def verificar_conectividad(self) -> Dict[str, Any]:
        """
        Verifica la conectividad con la API Apiaim
        
        Returns:
            Dict con estado de conectividad
        """
        try:
            logger.info("Verificando conectividad con API Apiaim")
            
            # Realizar una búsqueda simple para verificar conectividad
            resultado = await self.buscar_clientes(
                search="",
                pageSize=1
            )
            
            if resultado.get("success") is not False:
                return {
                    "conectado": True,
                    "mensaje": "Conectividad exitosa con API Apiaim",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "conectado": False,
                    "mensaje": "Error de conectividad con API Apiaim",
                    "error": resultado.get("error"),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error verificando conectividad: {e}")
            return {
                "conectado": False,
                "mensaje": "Error verificando conectividad",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def obtener_estadisticas_clientes(self, session: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de clientes
        
        Args:
            session: Sesión personalizada
            
        Returns:
            Dict con estadísticas de clientes
        """
        try:
            # Obtener clientes activos e inactivos
            activos = await self.buscar_clientes(active=True, pageSize=1000, session=session)
            inactivos = await self.buscar_clientes(active=False, pageSize=1000, session=session)
            
            estadisticas = {
                "total_clientes": 0,
                "clientes_activos": 0,
                "clientes_inactivos": 0,
                "tasa_actividad": 0.0
            }
            
            if activos.get("success"):
                estadisticas["clientes_activos"] = activos.get("dataLength", 0)
            
            if inactivos.get("success"):
                estadisticas["clientes_inactivos"] = inactivos.get("dataLength", 0)
            
            estadisticas["total_clientes"] = estadisticas["clientes_activos"] + estadisticas["clientes_inactivos"]
            
            if estadisticas["total_clientes"] > 0:
                estadisticas["tasa_actividad"] = (estadisticas["clientes_activos"] / estadisticas["total_clientes"]) * 100
            
            return {
                "success": True,
                "estadisticas": estadisticas,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                "success": False,
                "error": str(e),
                "estadisticas": {}
            }
    
    async def close(self):
        """Cierra el cliente HTTP"""
        await self.client.aclose()
        logger.info("ApiaimClient cerrado")
    
    def __del__(self):
        """Destructor para limpiar recursos"""
        try:
            if hasattr(self, 'client') and self.client:
                asyncio.create_task(self.client.aclose())
        except Exception:
            pass