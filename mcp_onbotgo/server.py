"""
Servidor MCP principal para OnBotGo Task Management

Este módulo implementa el servidor MCP que expone herramientas inteligentes
para la gestión de tareas, integración con APIs existentes y capacidades de IA.
"""

import asyncio
import logging
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.types import Tool, TextContent, CallToolRequest, CallToolResult
except ImportError:
    # Para casos donde MCP no está instalado
    print("Advertencia: MCP no está instalado. Instale con: pip install mcp")
    Server = None
    InitializationOptions = None
    Tool = None
    TextContent = None

from .config import get_config

# Configurar logging
logger = logging.getLogger(__name__)


class MockTaskManager:
    """Mock implementation para desarrollo sin dependencias"""
    
    def __init__(self, config, apiaim_client, intranet_client, ai_analyzer):
        self.config = config
        self.apiaim_client = apiaim_client
        self.intranet_client = intranet_client
        self.ai_analyzer = ai_analyzer
    
    async def crear_tarea_inteligente(self, **kwargs):
        return {
            "success": True,
            "message": "Tarea creada exitosamente (modo demo)",
            "tarea_id": 12345,
            "contexto_detectado": {
                "cliente_mencionado": False,
                "prioridad_inferida": "media",
                "categoria": "desarrollo"
            },
            "argumentos_recibidos": kwargs
        }
    
    async def buscar_tareas_semantica(self, **kwargs):
        return {
            "success": True,
            "resultados": [
                {
                    "id": 1001,
                    "titulo": "Optimizar performance del dashboard",
                    "descripcion": "Mejorar tiempos de carga",
                    "estado": "en_progreso",
                    "asignado_a": "Juan Pérez",
                    "cliente": "TechCorp"
                },
                {
                    "id": 1002,
                    "titulo": "Revisar logs de error",
                    "descripcion": "Analizar errores recurrentes",
                    "estado": "pendiente",
                    "asignado_a": "María González",
                    "cliente": "MegaCorp"
                }
            ],
            "total": 2,
            "query_original": kwargs.get('query', ''),
            "argumentos_recibidos": kwargs
        }
    
    async def actualizar_tarea_contextual(self, **kwargs):
        return {
            "success": True,
            "message": f"Tarea {kwargs.get('tarea_id')} actualizada exitosamente",
            "cambios_aplicados": kwargs.get('cambios', {}),
            "comentario_agregado": kwargs.get('comentario_automatico', True),
            "argumentos_recibidos": kwargs
        }


class MockClientManager:
    """Mock implementation para gestión de clientes"""
    
    def __init__(self, config, apiaim_client):
        self.config = config
        self.apiaim_client = apiaim_client
    
    async def buscar_cliente_inteligente(self, **kwargs):
        return {
            "success": True,
            "clientes_encontrados": [
                {
                    "id": "client_001",
                    "nombre": "TechCorp Solutions",
                    "estado": "activo",
                    "proyectos_activos": 3,
                    "score_match": 0.95
                }
            ],
            "query_original": kwargs.get('query', ''),
            "argumentos_recibidos": kwargs
        }
    
    async def obtener_historial_cliente(self, **kwargs):
        return {
            "success": True,
            "cliente_id": kwargs.get('cliente_id', ''),
            "historial": {
                "tareas_totales": 45,
                "tareas_completadas": 38,
                "promedio_tiempo_resolucion": "3.2 días",
                "satisfaccion_promedio": 4.7,
                "ultima_interaccion": "2025-06-01"
            },
            "argumentos_recibidos": kwargs
        }


class MockAnalyticsManager:
    """Mock implementation para análisis y métricas"""
    
    def __init__(self, config, apiaim_client, intranet_client):
        self.config = config
        self.apiaim_client = apiaim_client
        self.intranet_client = intranet_client
    
    async def analizar_productividad_equipo(self, **kwargs):
        return {
            "success": True,
            "periodo": kwargs.get('periodo', 'ultimo_mes'),
            "metricas": {
                "tareas_completadas": 127,
                "tareas_planificadas": 140,
                "porcentaje_completado": 90.7,
                "tiempo_promedio_tarea": "2.1 días",
                "equipo_productividad": "alta"
            },
            "tendencias": {
                "completado_vs_mes_anterior": "+12%",
                "tiempo_resolucion_tendencia": "-8%"
            },
            "recomendaciones": [
                "Continuar con el ritmo actual",
                "Considerar redistribución de tareas complejas"
            ],
            "argumentos_recibidos": kwargs
        }
    
    async def detectar_cuellos_botella(self, **kwargs):
        return {
            "success": True,
            "cuellos_detectados": [
                {
                    "tipo": "asignacion",
                    "descripcion": "Sobrecarga en desarrollador senior",
                    "impacto": "alto",
                    "solucion_sugerida": "Redistribuir 3 tareas a desarrolladores junior"
                }
            ],
            "proyecto_id": kwargs.get('proyecto_id', 'todos'),
            "argumentos_recibidos": kwargs
        }
    
    async def generar_reporte_proyecto(self, **kwargs):
        return {
            "success": True,
            "proyecto_id": kwargs.get('proyecto_id', ''),
            "reporte": {
                "resumen_ejecutivo": "Proyecto en buen estado, 85% completado",
                "tareas_total": 40,
                "tareas_completadas": 34,
                "tareas_pendientes": 6,
                "fecha_estimada_finalizacion": "2025-06-15",
                "riesgos_identificados": 1,
                "satisfaccion_cliente": 4.5
            },
            "formato": kwargs.get('formato', 'ejecutivo'),
            "argumentos_recibidos": kwargs
        }


class MCPOnBotGoServer:
    """Servidor MCP principal para OnBotGo"""
    
    def __init__(self):
        self.config = get_config()
        
        # Verificar si MCP está disponible
        if Server is None:
            logger.warning("MCP no disponible, usando modo demo")
            self.demo_mode = True
            self.server = None
        else:
            self.demo_mode = False
            self.server = Server(self.config.mcp_server_name)
        
        # Inicializar componentes mock (reemplazar con implementaciones reales)
        self.task_manager = MockTaskManager(self.config, None, None, None)
        self.client_manager = MockClientManager(self.config, None)
        self.analytics_manager = MockAnalyticsManager(self.config, None, None)
        
        # Registrar manejadores si MCP está disponible
        if not self.demo_mode:
            self._register_handlers()
        
        logger.info(f"Servidor MCP OnBotGo inicializado - v{self.config.mcp_server_version}")
        logger.info(f"Modo demo: {self.demo_mode}")
    
    def _register_handlers(self):
        """Registrar todos los manejadores MCP"""
        if self.demo_mode or self.server is None:
            return
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """Listar todas las herramientas disponibles"""
            return [
                Tool(
                    name="crear_tarea_inteligente",
                    description="Crea una nueva tarea con análisis inteligente de contexto",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "descripcion": {
                                "type": "string",
                                "description": "Descripción en lenguaje natural de la tarea"
                            },
                            "proyecto_id": {
                                "type": "string",
                                "description": "ID del proyecto o tablero"
                            }
                        },
                        "required": ["descripcion", "proyecto_id"]
                    }
                ),
                Tool(
                    name="buscar_tareas_semantica",
                    description="Búsqueda avanzada de tareas usando comprensión natural",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Consulta en lenguaje natural"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="analizar_productividad_equipo",
                    description="Análisis completo de productividad del equipo",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "periodo": {
                                "type": "string",
                                "enum": ["ultima_semana", "ultimo_mes", "ultimo_trimestre"]
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Manejar llamadas a herramientas"""
            try:
                logger.info(f"Ejecutando herramienta: {name}")
                
                # Enrutar a los managers apropiados
                if name == "crear_tarea_inteligente":
                    result = await self.task_manager.crear_tarea_inteligente(**arguments)
                elif name == "buscar_tareas_semantica":
                    result = await self.task_manager.buscar_tareas_semantica(**arguments)
                elif name == "actualizar_tarea_contextual":
                    result = await self.task_manager.actualizar_tarea_contextual(**arguments)
                elif name == "buscar_cliente_inteligente":
                    result = await self.client_manager.buscar_cliente_inteligente(**arguments)
                elif name == "obtener_historial_cliente":
                    result = await self.client_manager.obtener_historial_cliente(**arguments)
                elif name == "analizar_productividad_equipo":
                    result = await self.analytics_manager.analizar_productividad_equipo(**arguments)
                elif name == "detectar_cuellos_botella":
                    result = await self.analytics_manager.detectar_cuellos_botella(**arguments)
                elif name == "generar_reporte_proyecto":
                    result = await self.analytics_manager.generar_reporte_proyecto(**arguments)
                else:
                    result = {"error": f"Herramienta '{name}' no encontrada"}
                
                # Formatear resultado
                result_text = json.dumps(result, indent=2, ensure_ascii=False)
                
                return [TextContent(
                    type="text",
                    text=result_text
                )]
                
            except Exception as e:
                logger.error(f"Error ejecutando {name}: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    async def demo_call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Llamada de herramienta en modo demo"""
        logger.info(f"Demo: Ejecutando herramienta {name}")
        
        # Enrutar a los managers apropiados
        if name == "crear_tarea_inteligente":
            return await self.task_manager.crear_tarea_inteligente(**arguments)
        elif name == "buscar_tareas_semantica":
            return await self.task_manager.buscar_tareas_semantica(**arguments)
        elif name == "actualizar_tarea_contextual":
            return await self.task_manager.actualizar_tarea_contextual(**arguments)
        elif name == "buscar_cliente_inteligente":
            return await self.client_manager.buscar_cliente_inteligente(**arguments)
        elif name == "obtener_historial_cliente":
            return await self.client_manager.obtener_historial_cliente(**arguments)
        elif name == "analizar_productividad_equipo":
            return await self.analytics_manager.analizar_productividad_equipo(**arguments)
        elif name == "detectar_cuellos_botella":
            return await self.analytics_manager.detectar_cuellos_botella(**arguments)
        elif name == "generar_reporte_proyecto":
            return await self.analytics_manager.generar_reporte_proyecto(**arguments)
        else:
            return {"error": f"Herramienta '{name}' no encontrada"}
    
    async def run(self, transport_type: str = "stdio"):
        """Ejecutar el servidor MCP"""
        if self.demo_mode:
            logger.info("Ejecutando en modo demo - MCP no disponible")
            # En modo demo, solo mantenemos el servidor vivo
            while True:
                await asyncio.sleep(1)
        
        logger.info(f"Iniciando servidor MCP OnBotGo en modo {transport_type}")
        
        if transport_type == "stdio":
            from mcp.server.stdio import stdio_server
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name=self.config.mcp_server_name,
                        server_version=self.config.mcp_server_version
                    )
                )
        else:
            raise ValueError(f"Tipo de transporte no soportado: {transport_type}")


# Función principal
async def main():
    """Función principal para ejecutar el servidor MCP"""
    import sys
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Determinar tipo de transporte
    transport_type = "stdio"
    if len(sys.argv) > 1:
        transport_type = sys.argv[1]
    
    # Crear y ejecutar servidor
    server = MCPOnBotGoServer()
    
    if server.demo_mode:
        logger.info("=== MODO DEMO ===")
        logger.info("Para instalar MCP completo: pip install mcp")
        
        # Ejemplos de uso en modo demo
        ejemplos = [
            ("crear_tarea_inteligente", {
                "descripcion": "Revisar el dashboard de analytics para optimizar performance",
                "proyecto_id": "proyecto_001"
            }),
            ("buscar_tareas_semantica", {
                "query": "tareas pendientes de optimización"
            }),
            ("analizar_productividad_equipo", {
                "periodo": "ultimo_mes"
            })
        ]
        
        for herramienta, argumentos in ejemplos:
            logger.info(f"\n--- Ejemplo: {herramienta} ---")
            resultado = await server.demo_call_tool(herramienta, argumentos)
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
        
        logger.info("\n=== Servidor demo ejecutándose ===\nPresiona Ctrl+C para salir")
        await server.run(transport_type)
    else:
        await server.run(transport_type)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)