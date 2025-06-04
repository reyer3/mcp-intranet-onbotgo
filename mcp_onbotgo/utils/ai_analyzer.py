"""
Analizador de IA para MCP OnBotGo

Este módulo implementa capacidades de análisis con IA para procesamiento
de lenguaje natural, sentiment analysis y extracción de contexto.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Analizador de IA para procesamiento de texto y extracción de contexto"""
    
    def __init__(self, config):
        self.config = config
        self.openai_available = OPENAI_AVAILABLE and config.openai_api_key
        
        if self.openai_available:
            openai.api_key = config.openai_api_key
            self.model = config.openai_model
            self.max_tokens = config.max_tokens
            logger.info(f"AIAnalyzer inicializado con OpenAI - Modelo: {self.model}")
        else:
            logger.warning("AIAnalyzer inicializado sin OpenAI - usando análisis local")
        
        # Patrones para análisis local
        self.priority_patterns = {
            "critica": r"\b(urgente|crítico|emergencia|inmediato|ahora|ya|bloqueante)\b",
            "alta": r"\b(importante|prioridad|rápido|pronto|necesario)\b",
            "media": r"\b(normal|regular|cuando puedas|moderado)\b",
            "baja": r"\b(opcional|sugerencia|mejora|futuro|algún día)\b"
        }
        
        self.category_patterns = {
            "desarrollo": r"\b(código|programar|desarrollar|implementar|bug|error|api|backend|frontend)\b",
            "diseño": r"\b(diseño|ui|ux|mockup|prototipo|visual|interfaz|wireframe)\b",
            "qa": r"\b(test|testing|qa|prueba|verificar|validar|revisar)\b",
            "marketing": r"\b(marketing|contenido|social|campaña|promoción|seo)\b",
            "soporte": r"\b(soporte|ayuda|problema|incidencia|consulta|ticket)\b",
            "infraestructura": r"\b(servidor|base de datos|infraestructura|deploy|hosting|devops)\b"
        }
        
        self.client_patterns = [
            r"cliente\s+([A-Z][a-zá-ú]+(?:\s+[A-Z][a-zá-ú]+)*)",
            r"para\s+([A-Z][a-zá-ú]+(?:\s+[A-Z][a-zá-ú]+)*)",
            r"de\s+([A-Z][a-zá-ú]+(?:\s+[A-Z][a-zá-ú]+)*)",
            r"empresa\s+([A-Z][a-zá-ú]+(?:\s+[A-Z][a-zá-ú]+)*)"
        ]
    
    async def analyze_task_description(self, description: str) -> Dict[str, Any]:
        """
        Analiza una descripción de tarea para extraer contexto e intención
        
        Args:
            description: Descripción de la tarea en lenguaje natural
            
        Returns:
            Dict con análisis de contexto y metadatos
        """
        try:
            logger.info(f"Analizando descripción de tarea: {description[:50]}...")
            
            # Análisis local siempre disponible
            local_analysis = await self._analyze_locally(description)
            
            # Análisis con IA si está disponible
            ai_analysis = {}
            if self.openai_available and self.config.enable_ai_analysis:
                ai_analysis = await self._analyze_with_openai(description)
            
            # Combinar resultados
            combined_analysis = self._combine_analysis_results(local_analysis, ai_analysis)
            
            # Añadir metadatos
            combined_analysis.update({
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "analysis_methods": {
                    "local": True,
                    "ai": bool(ai_analysis),
                    "model_used": self.model if ai_analysis else None
                },
                "text_stats": self._calculate_text_stats(description)
            })
            
            return combined_analysis
            
        except Exception as e:
            logger.error(f"Error en analyze_task_description: {e}", exc_info=True)
            return {
                "error": str(e),
                "fallback_analysis": await self._analyze_locally(description)
            }
    
    async def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extrae entidades nombradas del texto (clientes, fechas, personas, etc.)
        
        Args:
            text: Texto a analizar
            
        Returns:
            Dict con entidades extraídas por categoría
        """
        try:
            entities = {
                "clients": [],
                "dates": [],
                "people": [],
                "technologies": [],
                "priorities": [],
                "actions": []
            }
            
            text_lower = text.lower()
            
            # Extraer clientes
            for pattern in self.client_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities["clients"].extend(matches)
            
            # Extraer fechas
            date_patterns = [
                r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
                r"\d{1,2}\s+de\s+\w+\s+de\s+\d{4}",
                r"(lunes|martes|miércoles|jueves|viernes|sábado|domingo)\s+próximo",
                r"(mañana|hoy|ayer|la\s+próxima\s+semana)"
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities["dates"].extend(matches)
            
            # Extraer tecnologías
            tech_keywords = [
                "react", "vue", "angular", "node", "python", "django", "flask",
                "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
                "aws", "azure", "gcp", "docker", "kubernetes", "jenkins"
            ]
            
            for tech in tech_keywords:
                if tech in text_lower:
                    entities["technologies"].append(tech)
            
            # Extraer verbos de acción
            action_patterns = [
                r"\b(crear|desarrollar|implementar|diseñar|testear|corregir|optimizar|revisar)\b"
            ]
            
            for pattern in action_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities["actions"].extend(matches)
            
            # Limpiar duplicados
            for key in entities:
                entities[key] = list(set(entities[key]))
            
            return entities
            
        except Exception as e:
            logger.error(f"Error en extract_entities: {e}")
            return {"error": str(e)}
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analiza el sentimiento del texto
        
        Args:
            text: Texto a analizar
            
        Returns:
            Dict con análisis de sentimiento
        """
        try:
            # Análisis básico de sentimiento usando palabras clave
            positive_words = [
                "excelente", "bueno", "genial", "perfecto", "satisfecho",
                "contento", "feliz", "positivo", "éxito", "logrado"
            ]
            
            negative_words = [
                "malo", "terrible", "problema", "error", "falla",
                "molesto", "frustrante", "difícil", "complicado", "urgente"
            ]
            
            urgent_words = [
                "urgente", "inmediato", "crítico", "emergencia",
                "ahora", "ya", "rápido", "pronto"
            ]
            
            text_lower = text.lower()
            
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            urgent_count = sum(1 for word in urgent_words if word in text_lower)
            
            # Calcular scores
            total_sentiment_words = positive_count + negative_count
            
            if total_sentiment_words == 0:
                sentiment = "neutral"
                confidence = 0.5
            elif positive_count > negative_count:
                sentiment = "positive"
                confidence = positive_count / total_sentiment_words
            else:
                sentiment = "negative"
                confidence = negative_count / total_sentiment_words
            
            urgency_level = "high" if urgent_count > 2 else "medium" if urgent_count > 0 else "low"
            
            return {
                "sentiment": sentiment,
                "confidence": confidence,
                "urgency_level": urgency_level,
                "urgency_score": urgent_count,
                "emotional_indicators": {
                    "positive_signals": positive_count,
                    "negative_signals": negative_count,
                    "urgency_signals": urgent_count
                }
            }
            
        except Exception as e:
            logger.error(f"Error en analyze_sentiment: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def suggest_title(self, description: str, max_length: int = 80) -> str:
        """
        Sugiere un título para una tarea basado en su descripción
        
        Args:
            description: Descripción de la tarea
            max_length: Longitud máxima del título
            
        Returns:
            Título sugerido
        """
        try:
            # Extraer primera oración o hasta el primer punto
            first_sentence = description.split('.')[0].strip()
            
            # Si es muy largo, buscar hasta la primera coma o punto y coma
            if len(first_sentence) > max_length:
                first_sentence = description.split(',')[0].strip()
                if len(first_sentence) > max_length:
                    first_sentence = description.split(';')[0].strip()
            
            # Si aún es muy largo, truncar y añadir puntos suspensivos
            if len(first_sentence) > max_length:
                first_sentence = first_sentence[:max_length-3] + "..."
            
            # Limpiar y capitalizar
            title = first_sentence.strip()
            if title and not title[0].isupper():
                title = title[0].upper() + title[1:]
            
            # Si no hay título válido, usar un genérico
            if not title or len(title) < 5:
                title = "Nueva tarea"
            
            return title
            
        except Exception as e:
            logger.error(f"Error en suggest_title: {e}")
            return "Nueva tarea"
    
    async def classify_complexity(self, description: str) -> Dict[str, Any]:
        """
        Clasifica la complejidad de una tarea
        
        Args:
            description: Descripción de la tarea
            
        Returns:
            Dict con clasificación de complejidad
        """
        try:
            complexity_indicators = {
                "simple": [
                    "cambiar", "actualizar", "corregir", "revisar", "verificar",
                    "texto", "color", "enlace", "imagen"
                ],
                "medium": [
                    "implementar", "desarrollar", "crear", "diseñar", "optimizar",
                    "integrar", "configurar", "refactorizar"
                ],
                "complex": [
                    "arquitectura", "sistema", "base de datos", "algoritmo",
                    "performance", "escalabilidad", "seguridad", "migración"
                ]
            }
            
            text_lower = description.lower()
            scores = {}
            
            for complexity, keywords in complexity_indicators.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                scores[complexity] = score
            
            # Determinar complejidad basada en scores
            if scores["complex"] > 0:
                complexity = "complex"
                estimated_hours = 16 + (scores["complex"] * 8)
            elif scores["medium"] > scores["simple"]:
                complexity = "medium"
                estimated_hours = 4 + (scores["medium"] * 2)
            else:
                complexity = "simple"
                estimated_hours = 1 + scores["simple"]
            
            # Factores adicionales de complejidad
            additional_factors = []
            
            if len(description) > 500:
                additional_factors.append("descripcion_detallada")
                estimated_hours += 2
            
            if re.search(r"\b(api|integración|terceros)\b", text_lower):
                additional_factors.append("integracion_externa")
                estimated_hours += 4
            
            if re.search(r"\b(test|testing|qa)\b", text_lower):
                additional_factors.append("requiere_testing")
                estimated_hours += 2
            
            return {
                "complexity": complexity,
                "estimated_hours": min(estimated_hours, 40),  # Cap a 40 horas
                "confidence": max(scores.values()) / len(complexity_indicators),
                "complexity_scores": scores,
                "additional_factors": additional_factors
            }
            
        except Exception as e:
            logger.error(f"Error en classify_complexity: {e}")
            return {
                "complexity": "medium",
                "estimated_hours": 4,
                "error": str(e)
            }
    
    # Métodos privados
    
    async def _analyze_locally(self, description: str) -> Dict[str, Any]:
        """Análisis local usando patrones y reglas"""
        analysis = {
            "priority": "media",
            "category": "general",
            "client_mentioned": False,
            "urgency_detected": False,
            "complexity": "medium",
            "estimated_hours": 4
        }
        
        text_lower = description.lower()
        
        # Detectar prioridad
        for priority, pattern in self.priority_patterns.items():
            if re.search(pattern, text_lower):
                analysis["priority"] = priority
                if priority in ["critica", "alta"]:
                    analysis["urgency_detected"] = True
                break
        
        # Detectar categoría
        for category, pattern in self.category_patterns.items():
            if re.search(pattern, text_lower):
                analysis["category"] = category
                break
        
        # Detectar mención de cliente
        for pattern in self.client_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                analysis["client_mentioned"] = True
                break
        
        # Análisis de complejidad
        complexity_analysis = await self.classify_complexity(description)
        analysis.update({
            "complexity": complexity_analysis["complexity"],
            "estimated_hours": complexity_analysis["estimated_hours"]
        })
        
        return analysis
    
    async def _analyze_with_openai(self, description: str) -> Dict[str, Any]:
        """Análisis usando OpenAI"""
        if not self.openai_available:
            return {}
        
        try:
            prompt = f"""
Analiza la siguiente descripción de tarea y extrae la siguiente información en formato JSON:

Descripción: "{description}"

Extrae:
1. priority: (critica, alta, media, baja)
2. category: (desarrollo, diseño, qa, marketing, soporte, infraestructura, general)
3. client_mentioned: (true/false)
4. urgency_detected: (true/false)
5. complexity: (simple, medium, complex)
6. estimated_hours: (número estimado de horas)
7. suggested_title: (título sugerido de máximo 60 caracteres)
8. key_actions: (lista de acciones principales identificadas)

Responde solo con el JSON, sin explicaciones adicionales.
"""
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto analizador de tareas de proyectos de software. Respondes solo en JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            # Intentar parsear JSON
            import json
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Error en análisis con OpenAI: {e}")
            return {}
    
    def _combine_analysis_results(self, local: Dict[str, Any], ai: Dict[str, Any]) -> Dict[str, Any]:
        """Combina resultados de análisis local y de IA"""
        # Usar IA como principal si está disponible, local como fallback
        if ai:
            combined = ai.copy()
            # Añadir campos que solo están en análisis local
            for key, value in local.items():
                if key not in combined:
                    combined[key] = value
        else:
            combined = local.copy()
        
        return combined
    
    def _calculate_text_stats(self, text: str) -> Dict[str, int]:
        """Calcula estadísticas del texto"""
        return {
            "character_count": len(text),
            "word_count": len(text.split()),
            "sentence_count": len([s for s in text.split('.') if s.strip()]),
            "paragraph_count": len([p for p in text.split('\n') if p.strip()])
        }