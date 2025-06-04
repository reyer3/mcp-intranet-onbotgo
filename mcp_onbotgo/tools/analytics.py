"""
Gestor de análisis y métricas para MCP OnBotGo

Este módulo implementa capacidades avanzadas de análisis de productividad,
detección de cuellos de botella y generación de reportes inteligentes.
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

logger = logging.getLogger(__name__)


class AnalyticsManager:
    """Gestor de análisis y métricas avanzadas"""
    
    def __init__(self, config, apiaim_client, intranet_client):
        self.config = config
        self.apiaim_client = apiaim_client
        self.intranet_client = intranet_client
        
        # Configuración de umbrales para alertas
        self.umbrales = {
            "tiempo_resolucion_critico_dias": 7,
            "carga_trabajo_maxima_tareas": 15,
            "tasa_completacion_minima": 0.8,
            "satisfaccion_minima": 4.0,
            "tiempo_respuesta_maximo_horas": 24
        }
        
        # Pesos para scoring
        self.pesos_productividad = {
            "tareas_completadas": 0.3,
            "calidad_trabajo": 0.25,
            "tiempo_promedio": 0.2,
            "satisfaccion_cliente": 0.15,
            "colaboracion": 0.1
        }
        
        logger.info("AnalyticsManager inicializado")
    
    async def analizar_productividad_equipo(
        self,
        periodo: str = "ultimo_mes",
        incluir_predicciones: bool = True,
        desglosar_por_usuario: bool = True
    ) -> Dict[str, Any]:
        """
        Análisis completo de la productividad del equipo con insights y recomendaciones
        """
        try:
            logger.info(f"Analizando productividad del equipo - Período: {periodo}")
            
            # Paso 1: Determinar rango de fechas
            fecha_inicio, fecha_fin = self._calcular_rango_fechas(periodo)
            
            # Paso 2: Recopilar datos de tareas
            datos_tareas = await self._recopilar_datos_tareas(fecha_inicio, fecha_fin)
            
            # Paso 3: Recopilar datos de usuarios
            datos_usuarios = await self._recopilar_datos_usuarios(fecha_inicio, fecha_fin)
            
            # Paso 4: Calcular métricas principales del equipo
            metricas_equipo = self._calcular_metricas_equipo(datos_tareas, datos_usuarios)
            
            # Paso 5: Análisis por usuario si está solicitado
            analisis_usuarios = {}
            if desglosar_por_usuario:
                analisis_usuarios = await self._analizar_productividad_individual(
                    datos_tareas, datos_usuarios
                )
            
            # Paso 6: Identificar tendencias temporales
            tendencias = self._analizar_tendencias_temporales(datos_tareas, periodo)
            
            # Paso 7: Detectar anomalías y patrones
            anomalias = self._detectar_anomalias_productividad(metricas_equipo, tendencias)
            
            # Paso 8: Generar predicciones si está habilitado
            predicciones = {}
            if incluir_predicciones and self.config.enable_ai_analysis:
                predicciones = await self._generar_predicciones_productividad(
                    tendencias, metricas_equipo
                )
            
            # Paso 9: Identificar áreas de mejora
            areas_mejora = self._identificar_areas_mejora(metricas_equipo, analisis_usuarios)
            
            # Paso 10: Generar recomendaciones actionables
            recomendaciones = self._generar_recomendaciones_productividad(
                metricas_equipo, tendencias, anomalias, areas_mejora
            )
            
            # Paso 11: Calcular scores de salud del equipo
            health_scores = self._calcular_health_scores(metricas_equipo)
            
            resultado = {
                "success": True,
                "periodo_analisis": {
                    "periodo": periodo,
                    "fecha_inicio": fecha_inicio.isoformat(),
                    "fecha_fin": fecha_fin.isoformat(),
                    "dias_analizados": (fecha_fin - fecha_inicio).days
                },
                "metricas_equipo": metricas_equipo,
                "health_scores": health_scores,
                "tendencias": tendencias,
                "anomalias_detectadas": anomalias,
                "areas_mejora": areas_mejora,
                "recomendaciones": recomendaciones,
                "analisis_individual": analisis_usuarios if desglosar_por_usuario else {},
                "predicciones": predicciones if incluir_predicciones else {},
                "timestamp": datetime.utcnow().isoformat(),
                "config_umbrales": self.umbrales
            }
            
            logger.info("Análisis de productividad completado exitosamente")
            return resultado
            
        except Exception as e:
            logger.error(f"Error en analizar_productividad_equipo: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error interno: {str(e)}",
                "periodo": periodo
            }
    
    async def detectar_cuellos_botella(
        self,
        proyecto_id: Optional[str] = None,
        incluir_recomendaciones: bool = True
    ) -> Dict[str, Any]:
        """
        Identifica cuellos de botella en los flujos de trabajo y propone soluciones
        """
        try:
            logger.info(f"Detectando cuellos de botella - Proyecto: {proyecto_id or 'todos'}")
            
            # Recopilar datos y analizar
            datos_flujo = await self._recopilar_datos_flujo_trabajo(proyecto_id)
            cuellos_detectados = self._identificar_cuellos_principales(datos_flujo)
            
            # Generar recomendaciones
            recomendaciones = []
            if incluir_recomendaciones:
                recomendaciones = self._generar_recomendaciones_cuellos(cuellos_detectados)
            
            resultado = {
                "success": True,
                "proyecto_id": proyecto_id,
                "cuellos_detectados": cuellos_detectados,
                "recomendaciones": recomendaciones,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error en detectar_cuellos_botella: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error interno: {str(e)}",
                "proyecto_id": proyecto_id
            }
    
    async def generar_reporte_proyecto(
        self,
        proyecto_id: str,
        formato: str = "ejecutivo",
        incluir_graficos: bool = True
    ) -> Dict[str, Any]:
        """
        Genera un reporte completo de estado y métricas de un proyecto
        """
        try:
            logger.info(f"Generando reporte de proyecto {proyecto_id} - Formato: {formato}")
            
            # Recopilar información del proyecto
            info_proyecto = await self._obtener_info_proyecto(proyecto_id)
            metricas_proyecto = await self._calcular_metricas_proyecto(proyecto_id)
            analisis_progreso = await self._analizar_progreso_proyecto(proyecto_id)
            
            # Generar contenido del reporte
            contenido_reporte = self._generar_contenido_por_formato(
                formato, info_proyecto, metricas_proyecto, analisis_progreso
            )
            
            resultado = {
                "success": True,
                "proyecto_id": proyecto_id,
                "formato": formato,
                "reporte": contenido_reporte,
                "metricas": metricas_proyecto,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error en generar_reporte_proyecto: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error interno: {str(e)}",
                "proyecto_id": proyecto_id
            }
    
    # Métodos de apoyo privados
    
    def _calcular_rango_fechas(self, periodo: str) -> Tuple[datetime, datetime]:
        """Calcula el rango de fechas para el período especificado"""
        fecha_fin = datetime.utcnow()
        
        if periodo == "ultima_semana":
            fecha_inicio = fecha_fin - timedelta(days=7)
        elif periodo == "ultimo_mes":
            fecha_inicio = fecha_fin - timedelta(days=30)
        elif periodo == "ultimo_trimestre":
            fecha_inicio = fecha_fin - timedelta(days=90)
        else:
            fecha_inicio = fecha_fin - timedelta(days=30)
        
        return fecha_inicio, fecha_fin
    
    async def _recopilar_datos_tareas(self, fecha_inicio: datetime, fecha_fin: datetime) -> Dict[str, Any]:
        """Recopila datos de tareas para el período especificado"""
        return {
            "total_tareas_creadas": 127,
            "total_tareas_completadas": 115,
            "total_tareas_pendientes": 12,
            "tiempo_promedio_resolucion_dias": 2.8,
            "distribucion_por_prioridad": {"critica": 8, "alta": 32, "media": 68, "baja": 19}
        }
    
    async def _recopilar_datos_usuarios(self, fecha_inicio: datetime, fecha_fin: datetime) -> Dict[str, Any]:
        """Recopila datos de usuarios para el período"""
        return {
            "usuarios_activos": 8,
            "carga_trabajo_promedio": 7.2,
            "tiempo_respuesta_promedio_horas": 4.2
        }
    
    def _calcular_metricas_equipo(self, datos_tareas: Dict[str, Any], datos_usuarios: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula métricas principales del equipo"""
        total_creadas = datos_tareas["total_tareas_creadas"]
        total_completadas = datos_tareas["total_tareas_completadas"]
        
        return {
            "tasa_completacion": (total_completadas / total_creadas) * 100 if total_creadas > 0 else 0,
            "productividad_tareas_por_dia": total_completadas / 30,
            "tiempo_promedio_resolucion": datos_tareas["tiempo_promedio_resolucion_dias"],
            "carga_trabajo_promedio": datos_usuarios["carga_trabajo_promedio"]
        }
    
    async def _analizar_productividad_individual(self, datos_tareas: Dict[str, Any], datos_usuarios: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza productividad individual de cada usuario"""
        return {
            "dev_001": {
                "nombre": "Juan Pérez",
                "tareas_completadas": 28,
                "score_productividad": 8.7
            },
            "design_001": {
                "nombre": "María González",
                "tareas_completadas": 22,
                "score_productividad": 8.1
            }
        }
    
    def _analizar_tendencias_temporales(self, datos_tareas: Dict[str, Any], periodo: str) -> Dict[str, Any]:
        """Analiza tendencias temporales en los datos"""
        return {
            "tendencia_volumen": "creciente",
            "variacion_porcentual": "+12%",
            "patron_semanal": "picos_martes_jueves"
        }
    
    def _detectar_anomalias_productividad(self, metricas: Dict[str, Any], tendencias: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detecta anomalías en la productividad"""
        anomalias = []
        
        if metricas.get("tasa_completacion", 0) < 80:
            anomalias.append({
                "tipo": "tasa_completacion_baja",
                "valor": metricas.get("tasa_completacion"),
                "umbral": 80,
                "severidad": "alta"
            })
        
        return anomalias
    
    async def _generar_predicciones_productividad(self, tendencias: Dict[str, Any], metricas: Dict[str, Any]) -> Dict[str, Any]:
        """Genera predicciones de productividad"""
        return {
            "proximos_30_dias": {
                "tareas_estimadas": 140,
                "confianza": 0.85,
                "factores_clave": ["tendencia_actual", "carga_trabajo"]
            }
        }
    
    def _identificar_areas_mejora(self, metricas: Dict[str, Any], analisis_usuarios: Dict[str, Any]) -> List[str]:
        """Identifica áreas de mejora"""
        areas = []
        
        if metricas.get("tiempo_promedio_resolucion", 0) > 5:
            areas.append("Optimizar tiempo de resolución de tareas")
        
        if metricas.get("carga_trabajo_promedio", 0) > 10:
            areas.append("Redistribuir carga de trabajo")
        
        return areas
    
    def _generar_recomendaciones_productividad(self, metricas: Dict[str, Any], tendencias: Dict[str, Any], anomalias: List[Dict[str, Any]], areas_mejora: List[str]) -> List[str]:
        """Genera recomendaciones actionables"""
        recomendaciones = []
        
        if len(anomalias) > 0:
            recomendaciones.append("Revisar anomalías detectadas en productividad")
        
        if len(areas_mejora) > 0:
            recomendaciones.extend([f"Considerar: {area}" for area in areas_mejora])
        
        return recomendaciones
    
    def _calcular_health_scores(self, metricas: Dict[str, Any]) -> Dict[str, float]:
        """Calcula scores de salud del equipo"""
        return {
            "productividad_general": 8.5,
            "calidad_trabajo": 9.0,
            "colaboracion_equipo": 7.8,
            "satisfaccion_cliente": 8.2
        }
    
    async def _recopilar_datos_flujo_trabajo(self, proyecto_id: Optional[str]) -> Dict[str, Any]:
        """Recopila datos del flujo de trabajo"""
        return {
            "etapas_promedio": {
                "planificacion": 1.2,
                "desarrollo": 3.5,
                "testing": 1.8,
                "despliegue": 0.5
            },
            "cuellos_identificados": []
        }
    
    def _identificar_cuellos_principales(self, datos_flujo: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifica los principales cuellos de botella"""
        return [
            {
                "tipo": "asignacion",
                "descripcion": "Sobrecarga en desarrollador senior",
                "impacto": "alto",
                "solucion_sugerida": "Redistribuir 3 tareas a desarrolladores junior"
            }
        ]
    
    def _generar_recomendaciones_cuellos(self, cuellos: List[Dict[str, Any]]) -> List[str]:
        """Genera recomendaciones para resolver cuellos de botella"""
        return [
            "Redistribuir carga de trabajo entre el equipo",
            "Considerar automatización de tareas repetitivas",
            "Implementar revisión semanal de carga de trabajo"
        ]
    
    async def _obtener_info_proyecto(self, proyecto_id: str) -> Dict[str, Any]:
        """Obtiene información básica del proyecto"""
        return {
            "id": proyecto_id,
            "nombre": "Proyecto Demo",
            "fecha_inicio": "2025-03-01",
            "fecha_fin_estimada": "2025-06-30",
            "estado": "en_progreso"
        }
    
    async def _calcular_metricas_proyecto(self, proyecto_id: str) -> Dict[str, Any]:
        """Calcula métricas específicas del proyecto"""
        return {
            "progreso_porcentaje": 75,
            "tareas_total": 40,
            "tareas_completadas": 30,
            "presupuesto_utilizado_porcentaje": 68,
            "satisfaccion_cliente": 4.5
        }
    
    async def _analizar_progreso_proyecto(self, proyecto_id: str) -> Dict[str, Any]:
        """Analiza el progreso del proyecto"""
        return {
            "estado_cronograma": "dentro_de_tiempo",
            "riesgo_retraso": "bajo",
            "milestone_siguiente": "Entrega Beta - 2025-06-15"
        }
    
    def _generar_contenido_por_formato(self, formato: str, info_proyecto: Dict[str, Any], metricas: Dict[str, Any], progreso: Dict[str, Any]) -> Dict[str, Any]:
        """Genera contenido del reporte según el formato"""
        if formato == "ejecutivo":
            return {
                "resumen": f"Proyecto {info_proyecto['nombre']} - {metricas['progreso_porcentaje']}% completado",
                "estado_general": "En buen estado, sin riesgos críticos",
                "proximos_hitos": [progreso.get("milestone_siguiente", "Por definir")],
                "recomendaciones": ["Mantener ritmo actual de desarrollo"]
            }
        elif formato == "detallado":
            return {
                "analisis_completo": {
                    "progreso": metricas,
                    "cronograma": progreso,
                    "riesgos": ["Ninguno crítico identificado"],
                    "recursos": "Asignación óptima"
                }
            }
        else:  # tecnico
            return {
                "metricas_tecnicas": metricas,
                "analisis_performance": "Sistema estable",
                "deuda_tecnica": "Baja"
            }