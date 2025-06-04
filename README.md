# MCP Intranet OnBotGo

## 🚀 Model Context Protocol Server para Administración Inteligente de Tareas

Este proyecto implementa un servidor MCP (Model Context Protocol) que revoluciona la gestión de tareas del equipo OnBotGo, integrando sus APIs existentes de Apiaim e Intranet con capacidades avanzadas de IA.

## ✨ Características Principales

### 🎯 Gestión Inteligente de Tareas
- **Creación automática** de tareas desde descripción en lenguaje natural
- **Asignación inteligente** basada en carga de trabajo y expertise
- **Detección automática** de clientes y proyectos relacionados
- **Gestión de dependencias** y flujos de trabajo complejos

### 🔐 Autenticación Robusta
- Integración completa con **Google Identity Toolkit**
- **OAuth 2.1** para máxima seguridad
- **Gestión de permisos** granular por rol
- **Sesiones persistentes** con MCP

### 🤖 Capacidades de IA
- **Análisis semántico** de descripciones de tareas
- **Priorización automática** basada en contexto
- **Sugerencias inteligentes** de asignación
- **Detección de conflictos** y dependencias

### 🔄 Integración con APIs Existentes
- **BuscarClientes** - Búsqueda y asociación automática
- **CrearTareaEnTablero** - Creación optimizada de tareas
- **ActualizarTareaEnTablero** - Actualizaciones inteligentes
- **AgregarComentarioATarea** - Comentarios contextuales
- **Gestión de usuarios** completa

## 🚀 Instalación Rápida

### 1. Clonar el Repositorio
```bash
git clone https://github.com/reyer3/mcp-intranet-onbotgo.git
cd mcp-intranet-onbotgo
```

### 2. Configurar Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configuración de Variables de Entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 5. Ejecutar el Servidor
```bash
python -m mcp_onbotgo.server
```

## 📈 Métricas de Éxito

### KPIs Objetivos
- ⚡ **50% reducción** en tiempo de creación de tareas
- 📈 **25% aumento** en tasa de finalización de proyectos
- 🎯 **30% mejora** en precisión de asignaciones
- ⏱️ **<200ms** tiempo de respuesta promedio
- 😊 **>8.5 NPS** satisfacción del usuario

## 🤝 Soporte y Comunidad

### Reportar Problemas
- 🐛 [Issues en GitHub](https://github.com/reyer3/mcp-intranet-onbotgo/issues)
- 💬 [Discusiones](https://github.com/reyer3/mcp-intranet-onbotgo/discussions)

### Contribuir
1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

**🚀 ¡Transforma la gestión de tareas de tu equipo con IA!**

Para más información: [Documentación Completa](./docs/) | [Guía de Inicio Rápido](./docs/quickstart.md)
