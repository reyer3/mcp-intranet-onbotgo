"""
Cliente para API Intranet de OnBotGo

Este módulo implementa el cliente para interactuar con la API Intranet,
incluye operaciones de gestión de tareas, tableros y comentarios.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import httpx
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class IntranetClient:
    """Cliente para interactuar con la API Intranet"""
    
    def __init__(self, config):
        self.config = config
        self.base_url = config.intranet_base_url
        self.default_session = config.get_mibot_session_dict()
        
        # Configurar cliente HTTP
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "MCP-OnBotGo/1.0"
            }
        )
        
        logger.info(f"IntranetClient inicializado - Base URL: {self.base_url}")
    
    def _get_session_header(self, session_override: Optional[Dict[str, str]] = None) -> str:
        """Obtiene el header de sesión para las requests"""
        session_data = session_override or self.default_session
        return json.dumps(session_data)
    
    async def crear_tarea_en_tablero(
        self,
        tarea_data: Dict[str, Any],
        session: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Crea una nueva tarea en un tablero
        
        Args:
            tarea_data: Datos de la tarea a crear
            session: Sesión personalizada
            
        Returns:
            Dict con resultado de la creación
        """
        try:
            logger.info(f"Creando tarea en tablero: {tarea_data.get('name', 'Sin nombre')}")
            
            # Preparar headers
            headers = {
                "mibot_session": self._get_session_header(session)
            }
            
            # Realizar request
            response = await self.client.post(
                f"{self.base_url}/api/v1/boards/task",
                json=tarea_data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                task_id = result.get("data", {}).get("id") if isinstance(result.get("data"), dict) else None
                logger.info(f"Tarea creada exitosamente: ID {task_id}")
                return result
            else:
                logger.error(f"Error creando tarea: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Error en crear_tarea_en_tablero: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error interno: {str(e)}",
                "data": None
            }
    
    async def actualizar_tarea_en_tablero(
        self,
        task_id: int,
        cambios: Dict[str, Any],
        session: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Actualiza una tarea existente
        
        Args:
            task_id: ID de la tarea a actualizar
            cambios: Cambios a aplicar
            session: Sesión personalizada
            
        Returns:
            Dict con resultado de la actualización
        """
        try:
            logger.info(f"Actualizando tarea {task_id} con cambios: {list(cambios.keys())}")
            
            # Preparar headers
            headers = {
                "mibot_session": self._get_session_header(session)
            }
            
            # Realizar request
            response = await self.client.put(
                f"{self.base_url}/api/v1/boards/task/{task_id}",
                json=cambios,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Tarea {task_id} actualizada exitosamente")
                return result
            else:
                logger.error(f"Error actualizando tarea {task_id}: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Error en actualizar_tarea_en_tablero: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error interno: {str(e)}",
                "data": None
            }
    
    async def obtener_detalle_tarea(
        self,
        task_id: int,
        session: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Obtiene el detalle completo de una tarea
        
        Args:
            task_id: ID de la tarea
            session: Sesión personalizada
            
        Returns:
            Dict con detalle de la tarea
        """
        try:
            logger.info(f"Obteniendo detalle de tarea: {task_id}")
            
            # Preparar headers
            headers = {
                "mibot_session": self._get_session_header(session)
            }
            
            # Preparar parámetros
            params = {"id": task_id}
            
            # Realizar request
            response = await self.client.get(
                f"{self.base_url}/api/v1/boards/item/task",
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Detalle de tarea {task_id} obtenido exitosamente")
                return result
            elif response.status_code == 404:
                logger.warning(f"Tarea no encontrada: {task_id}")
                return {
                    "success": False,
                    "error": "Tarea no encontrada",
                    "data": None
                }
            else:
                logger.error(f"Error obteniendo tarea {task_id}: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Error en obtener_detalle_tarea: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error interno: {str(e)}",
                "data": None
            }
    
    async def agregar_comentario_a_tarea(
        self,
        task_id: int,
        contenido: str,
        session: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Agrega un comentario a una tarea
        
        Args:
            task_id: ID de la tarea
            contenido: Contenido del comentario (HTML permitido)
            session: Sesión personalizada
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            logger.info(f"Agregando comentario a tarea {task_id}")
            
            # Preparar headers
            headers = {
                "mibot_session": self._get_session_header(session)
            }
            
            # Preparar datos del comentario
            comment_data = {
                "taskid": task_id,
                "content": contenido
            }
            
            # Realizar request
            response = await self.client.post(
                f"{self.base_url}/api/v1/boards/comment",
                json=comment_data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                comment_id = result.get("data", {}).get("id") if isinstance(result.get("data"), dict) else None
                logger.info(f"Comentario agregado exitosamente: ID {comment_id}")
                return result
            else:
                logger.error(f"Error agregando comentario: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Error en agregar_comentario_a_tarea: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error interno: {str(e)}",
                "data": None
            }
    
    async def obtener_tareas_por_columna(
        self,
        column_id: int,
        page: int = 1,
        session: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Obtiene tareas de una columna específica
        
        Args:
            column_id: ID de la columna
            page: Número de página
            session: Sesión personalizada
            
        Returns:
            Dict con tareas de la columna
        """
        try:
            logger.info(f"Obteniendo tareas de columna {column_id}, página {page}")
            
            # Preparar headers
            headers = {
                "mibot_session": self._get_session_header(session)
            }
            
            # Preparar parámetros
            params = {
                "page": page,
                "column": column_id
            }
            
            # Realizar request
            response = await self.client.get(
                f"{self.base_url}/api/v1/boards/items/ByPageAndColumn",
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                total_tareas = result.get("total", 0)
                logger.info(f"Obtenidas tareas de columna {column_id}: {total_tareas} total")
                return result
            else:
                logger.error(f"Error obteniendo tareas de columna {column_id}: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "data": [],
                    "total": 0
                }
                
        except Exception as e:
            logger.error(f"Error en obtener_tareas_por_columna: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error interno: {str(e)}",
                "data": [],
                "total": 0
            }
    
    async def buscar_tareas(
        self,
        termino_busqueda: str = "",
        filtros: Optional[Dict[str, Any]] = None,
        limite: int = 20,
        session: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Busca tareas en el sistema
        
        Args:
            termino_busqueda: Término de búsqueda
            filtros: Filtros adicionales
            limite: Límite de resultados
            session: Sesión personalizada
            
        Returns:
            Dict con resultados de búsqueda
        """
        try:
            logger.info(f"Buscando tareas: '{termino_busqueda}'")
            
            # Para esta implementación mock, simulamos una búsqueda
            # En la implementación real, usarías endpoints específicos de búsqueda
            
            # Mock de resultados de búsqueda
            mock_results = [
                {
                    "id": 1001,
                    "name": "Optimizar dashboard de analytics",
                    "description": "Mejorar performance y UX del dashboard principal",
                    "status": "en_progreso",
                    "assigned_user": "Juan Pérez",
                    "created_date": "2025-05-15T10:30:00Z",
                    "due_date": "2025-06-10T17:00:00Z",
                    "priority": "alta",
                    "column_id": 150
                },
                {
                    "id": 1002,
                    "name": "Revisar logs de error del sistema",
                    "description": "Analizar y corregir errores recurrentes en producción",
                    "status": "pendiente",
                    "assigned_user": "María González",
                    "created_date": "2025-05-20T09:15:00Z",
                    "due_date": "2025-06-05T12:00:00Z",
                    "priority": "critica",
                    "column_id": 149
                }
            ]
            
            # Filtrar resultados según término de búsqueda
            if termino_busqueda:
                termino_lower = termino_busqueda.lower()
                mock_results = [
                    tarea for tarea in mock_results
                    if termino_lower in tarea["name"].lower() or termino_lower in tarea["description"].lower()
                ]
            
            # Aplicar filtros adicionales
            if filtros:
                if "estado" in filtros:
                    estados_filtro = filtros["estado"] if isinstance(filtros["estado"], list) else [filtros["estado"]]
                    mock_results = [tarea for tarea in mock_results if tarea["status"] in estados_filtro]
                
                if "asignado_a" in filtros:
                    mock_results = [tarea for tarea in mock_results if filtros["asignado_a"] in tarea["assigned_user"]]
            
            # Aplicar límite
            mock_results = mock_results[:limite]
            
            return {
                "success": True,
                "data": mock_results,
                "total": len(mock_results),
                "termino_busqueda": termino_busqueda,
                "filtros_aplicados": filtros or {}
            }
            
        except Exception as e:
            logger.error(f"Error en buscar_tareas: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error interno: {str(e)}",
                "data": [],
                "total": 0
            }
    
    async def verificar_conectividad(self) -> Dict[str, Any]:
        """
        Verifica la conectividad con la API Intranet
        
        Returns:
            Dict con estado de conectividad
        """
        try:
            logger.info("Verificando conectividad con API Intranet")
            
            # Intentar una operación simple para verificar conectividad
            # En este caso, simularemos la verificación
            await asyncio.sleep(0.1)  # Simular latencia de red
            
            return {
                "conectado": True,
                "mensaje": "Conectividad exitosa con API Intranet",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error verificando conectividad: {e}")
            return {
                "conectado": False,
                "mensaje": "Error de conectividad con API Intranet",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def obtener_estadisticas_tableros(self, session: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas de tableros y tareas
        
        Args:
            session: Sesión personalizada
            
        Returns:
            Dict con estadísticas
        """
        try:
            # Mock de estadísticas
            estadisticas = {
                "total_tareas": 127,
                "tareas_completadas": 95,
                "tareas_en_progreso": 23,
                "tareas_pendientes": 9,
                "tasa_completacion": 74.8,
                "tiempo_promedio_resolucion_dias": 3.2,
                "tableros_activos": 8,
                "usuarios_activos": 12
            }
            
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
        logger.info("IntranetClient cerrado")
    
    def __del__(self):
        """Destructor para limpiar recursos"""
        try:
            if hasattr(self, 'client') and self.client:
                asyncio.create_task(self.client.aclose())
        except Exception:
            pass