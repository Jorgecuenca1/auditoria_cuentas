import requests
import json
from django.conf import settings
from typing import List, Dict, Optional


class OpenRouterChatbotService:
    def __init__(self):
        self.api_key = "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"
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "anthropic/claude-3-haiku"  # Modelo gratuito de OpenRouter
        
        # Base de conocimiento por rol
        self.knowledge_base = {
            'IPS': {
                'context': """
                Eres un asistente especializado en ayudar a usuarios IPS (Instituciones Prestadoras de Servicios de Salud) 
                en el sistema de auditoría de cuentas médicas. Tu función es responder preguntas sobre:
                
                - Cómo responder glosas
                - Cómo subir documentos de soporte
                - Cómo ver el estado de las facturas
                - Cómo acceder al historial de glosas
                - Procesos de auditoría desde la perspectiva de la IPS
                - Cómo interpretar las decisiones de la ET
                - Cómo manejar devoluciones de facturas
                
                Responde de manera clara, concisa y amigable. Usa ejemplos prácticos cuando sea posible.
                """,
                'examples': [
                    "¿Cómo respondo una glosa?",
                    "¿Dónde subo los documentos de soporte?",
                    "¿Cómo veo el historial de mis glosas?",
                    "¿Qué significa que mi factura fue devuelta?",
                    "¿Cómo sé si la ET aceptó mi respuesta?"
                ]
            },
            'ET': {
                'context': """
                Eres un asistente especializado en ayudar a usuarios ET (Entidad Territorial) 
                en el sistema de auditoría de cuentas médicas. Tu función es responder preguntas sobre:
                
                - Cómo auditar facturas
                - Cómo crear glosas
                - Cómo decidir sobre respuestas de IPS
                - Cómo generar reportes
                - Cómo devolver facturas
                - Cómo interpretar el historial de glosas
                - Procesos de auditoría y control
                
                Responde de manera técnica pero comprensible. Incluye pasos específicos cuando sea necesario.
                """,
                'examples': [
                    "¿Cómo creo una glosa?",
                    "¿Cómo decido si acepto la respuesta de una IPS?",
                    "¿Cómo genero reportes de auditoría?",
                    "¿Cómo veo el historial completo de una glosa?",
                    "¿Cuándo debo devolver una factura?"
                ]
            },
            'AUDITOR': {
                'context': """
                Eres un asistente especializado en ayudar a auditores 
                en el sistema de auditoría de cuentas médicas. Tu función es responder preguntas sobre:
                
                - Cómo realizar auditorías
                - Cómo revisar glosas
                - Cómo generar reportes detallados
                - Cómo analizar el historial de cambios
                - Cómo finalizar auditorías
                - Cómo interpretar datos de auditoría
                - Procesos de control y verificación
                
                Responde de manera profesional y técnica. Incluye detalles sobre procesos de auditoría.
                """,
                'examples': [
                    "¿Cómo realizo una auditoría completa?",
                    "¿Cómo reviso el historial de una glosa?",
                    "¿Cómo genero reportes de auditoría?",
                    "¿Cómo finalizo una auditoría?",
                    "¿Cómo interpreto los datos de auditoría?"
                ]
            },
            'EPS': {
                'context': """
                Eres un asistente especializado en ayudar a usuarios EPS (Entidades Promotoras de Salud) 
                en el sistema de auditoría de cuentas médicas. Tu función es responder preguntas sobre:
                
                - Cómo revisar facturas
                - Cómo ver el estado de auditorías
                - Cómo acceder a reportes
                - Cómo interpretar resultados de auditoría
                - Cómo ver el historial de glosas
                - Procesos de pago y cartera
                
                Responde de manera clara y orientada a la gestión. Enfócate en la información relevante para EPS.
                """,
                'examples': [
                    "¿Cómo veo el estado de mis facturas?",
                    "¿Cómo accedo a los reportes de auditoría?",
                    "¿Cómo interpreto los resultados de auditoría?",
                    "¿Cómo veo el historial de glosas?",
                    "¿Cómo calculo mi cartera?"
                ]
            }
        }

    def get_response(self, message: str, role: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Genera una respuesta usando OpenRouter basada en el rol del usuario y el historial de conversación
        """
        if role not in self.knowledge_base:
            return "Lo siento, no tengo información específica para tu rol. Por favor contacta al administrador."
        
        # Construir el prompt con contexto y historial
        context = self.knowledge_base[role]['context']
        
        # Agregar historial de conversación si existe
        history_context = ""
        if conversation_history:
            history_context = "\n\nHistorial de la conversación:\n"
            for msg in conversation_history[-5:]:  # Últimos 5 mensajes
                history_context += f"Usuario: {msg['message']}\n"
                history_context += f"Asistente: {msg['response']}\n"
        
        # Construir el prompt completo
        system_prompt = f"""
        {context}
        
        {history_context}
        
        Responde de manera útil, clara y específica para el rol de {role}. 
        Si la pregunta no está relacionada con el sistema de auditoría de cuentas médicas, 
        indícalo amablemente y sugiere hacer preguntas relacionadas con el sistema.
        """
        
        try:
            # Preparar la petición a OpenRouter
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://auditoria-cuentas.com",
                "X-Title": "Sistema de Auditoría de Cuentas Médicas",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            print(f"Enviando petición a OpenRouter con modelo {self.model}")
            response = requests.post(
                url=self.api_url,
                headers=headers,
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                print(f"Respuesta de OpenRouter: {ai_response[:200]}...")
                return ai_response
            else:
                print(f"Error en OpenRouter API: {response.status_code} - {response.text}")
                return self._get_fallback_response(message, role)
                
        except Exception as e:
            print(f"Error en OpenRouter: {str(e)}")
            return self._get_fallback_response(message, role)

    def _get_fallback_response(self, message: str, role: str) -> str:
        """Respuestas de fallback cuando la API no está disponible"""
        if role == 'IPS':
            if "manual" in message.lower() or "ayuda" in message.lower():
                return """**Manual de Usuario para IPS - Sistema de Auditoría de Cuentas Médicas**

**1. Navegación Principal:**
- **Radicados**: Ver todas las facturas radicadas para tu IPS
- **Glosas**: Gestionar glosas recibidas y respuestas
- **Devoluciones**: Ver facturas devueltas por la ET
- **Reportes**: Acceder a reportes específicos de tu IPS

**2. Responder Glosas:**
1. Ve a "Glosas" → "Glosas Pendientes"
2. Busca la glosa que quieres responder
3. Haz clic en "Responder"
4. Completa el formulario con:
   - Respuesta detallada a la glosa
   - Documentos de soporte (opcional)
   - Justificación técnica
5. Haz clic en "Enviar Respuesta"

**3. Ver Estado de Facturas:**
- Ve a "Radicados" para ver el estado de todas tus facturas
- Los estados posibles son: Radicada, En Auditoría, Con Glosas, Aprobada, Devuelta

**4. Historial de Glosas:**
- En cada glosa puedes ver el historial completo de cambios
- Haz clic en el ícono de historial para ver todos los movimientos

**5. Documentos de Soporte:**
- Puedes subir documentos al responder glosas
- Formatos aceptados: PDF, JPG, PNG
- Tamaño máximo: 10MB por archivo

¿Te gustaría que profundice en algún tema específico?"""
            elif "responder glosa" in message.lower():
                return """**Cómo Responder una Glosa - Paso a Paso:**

1. **Accede a las Glosas:**
   - Ve al menú principal → "Glosas" → "Glosas Pendientes"

2. **Encuentra la Glosa:**
   - Usa los filtros para buscar por número de factura, fecha, etc.
   - Haz clic en "Responder" en la glosa que quieres contestar

3. **Completa la Respuesta:**
   - Explica detalladamente por qué no estás de acuerdo con la glosa
   - Adjunta documentos de soporte si los tienes
   - Incluye justificación técnica y legal

4. **Enviar Respuesta:**
   - Revisa que toda la información esté completa
   - Haz clic en "Enviar Respuesta"

**Consejos importantes:**
- Sé específico y detallado en tu respuesta
- Incluye referencias a normativas si aplica
- Adjunta toda la documentación de soporte disponible
- Responde dentro del plazo establecido

¿Necesitas ayuda con algún paso específico?"""
            else:
                return "Hola! Soy tu asistente para el sistema de auditoría de cuentas médicas. Como IPS, puedo ayudarte con:\n\n- Responder glosas\n- Ver estado de facturas\n- Subir documentos\n- Acceder a reportes\n- Ver historial de glosas\n\n¿En qué puedo ayudarte hoy?"

        elif role == 'ET':
            if "crear glosa" in message.lower():
                return """**Cómo Crear una Glosa - Paso a Paso:**

1. **Accede a la Auditoría:**
   - Ve al menú principal → "Auditoría" → "Radicados"

2. **Selecciona la Factura:**
   - Busca la factura que quieres auditar
   - Haz clic en "Auditar Factura"

3. **Revisa los Detalles:**
   - Revisa todos los servicios facturados
   - Identifica los items que requieren glosa

4. **Crear Glosa:**
   - Haz clic en "Crear Glosa" en el item específico
   - Selecciona el tipo de glosa
   - Completa la justificación
   - Adjunta documentos de soporte si es necesario

5. **Guardar Glosa:**
   - Revisa que toda la información esté correcta
   - Haz clic en "Guardar Glosa"

**Tipos de Glosas Disponibles:**
- **Técnica**: Problemas con códigos, descripciones, etc.
- **Administrativa**: Documentación faltante o incorrecta
- **Económica**: Valores no autorizados o incorrectos

¿Necesitas ayuda con algún paso específico?"""
            else:
                return "Hola! Soy tu asistente para el sistema de auditoría de cuentas médicas. Como ET, puedo ayudarte con:\n\n- Crear glosas\n- Auditar facturas\n- Decidir sobre respuestas de IPS\n- Generar reportes\n- Devolver facturas\n\n¿En qué puedo ayudarte hoy?"

        elif role == 'AUDITOR':
            return "Hola! Soy tu asistente para el sistema de auditoría de cuentas médicas. Como Auditor, puedo ayudarte con:\n\n- Realizar auditorías completas\n- Revisar glosas y respuestas\n- Generar reportes detallados\n- Analizar historiales\n- Finalizar auditorías\n\n¿En qué puedo ayudarte hoy?"

        elif role == 'EPS':
            return "Hola! Soy tu asistente para el sistema de auditoría de cuentas médicas. Como EPS, puedo ayudarte con:\n\n- Revisar estado de facturas\n- Ver resultados de auditorías\n- Acceder a reportes\n- Interpretar glosas\n- Gestionar cartera\n\n¿En qué puedo ayudarte hoy?"

        return "Hola! Soy tu asistente para el sistema de auditoría de cuentas médicas. ¿En qué puedo ayudarte hoy?"

    def get_welcome_message(self, role: str) -> str:
        """Genera un mensaje de bienvenida personalizado según el rol"""
        if role == 'IPS':
            return """¡Hola! 👋 Soy tu asistente virtual especializado en el sistema de auditoría de cuentas médicas.

Como **IPS**, puedo ayudarte con:

🔍 **Consultas sobre Glosas:**
- Cómo responder glosas de manera efectiva
- Qué documentos subir como soporte
- Cómo interpretar las decisiones de la ET

📊 **Estado de Facturas:**
- Ver el estado actual de tus facturas
- Entender los diferentes estados del proceso
- Acceder al historial completo

📋 **Procesos y Procedimientos:**
- Guías paso a paso para cada proceso
- Mejores prácticas para responder glosas
- Cómo manejar devoluciones

💡 **Consejos y Recomendaciones:**
- Optimizar tus respuestas a glosas
- Documentación recomendada
- Plazos y tiempos importantes

¿En qué puedo ayudarte hoy? Puedes preguntarme sobre cualquier aspecto del sistema de auditoría."""
        
        elif role == 'ET':
            return """¡Hola! 👋 Soy tu asistente virtual especializado en el sistema de auditoría de cuentas médicas.

Como **ET**, puedo ayudarte con:

🔍 **Auditoría de Facturas:**
- Cómo realizar auditorías efectivas
- Crear glosas con justificación técnica
- Revisar respuestas de IPS

📊 **Gestión de Glosas:**
- Decidir sobre respuestas de IPS
- Aprobar o rechazar justificaciones
- Gestionar el flujo de glosas

📋 **Reportes y Análisis:**
- Generar reportes de auditoría
- Analizar tendencias y estadísticas
- Exportar datos para análisis

⚖️ **Control y Verificación:**
- Devolver facturas cuando sea necesario
- Establecer criterios de auditoría
- Mantener estándares de calidad

¿En qué puedo ayudarte hoy? Puedes preguntarme sobre cualquier aspecto del proceso de auditoría."""
        
        elif role == 'AUDITOR':
            return """¡Hola! 👋 Soy tu asistente virtual especializado en el sistema de auditoría de cuentas médicas.

Como **Auditor**, puedo ayudarte con:

🔍 **Auditorías Completas:**
- Procesos de auditoría paso a paso
- Revisión exhaustiva de facturas
- Análisis de documentación

📊 **Gestión de Glosas:**
- Crear glosas técnicas y administrativas
- Revisar respuestas de IPS
- Tomar decisiones informadas

📋 **Reportes Detallados:**
- Generar reportes de auditoría
- Analizar historiales completos
- Documentar hallazgos

⚖️ **Control de Calidad:**
- Verificar cumplimiento normativo
- Establecer criterios de auditoría
- Finalizar auditorías correctamente

¿En qué puedo ayudarte hoy? Puedes preguntarme sobre cualquier aspecto técnico del proceso de auditoría."""
        
        elif role == 'EPS':
            return """¡Hola! 👋 Soy tu asistente virtual especializado en el sistema de auditoría de cuentas médicas.

Como **EPS**, puedo ayudarte con:

🔍 **Seguimiento de Facturas:**
- Ver el estado actual de tus facturas
- Revisar resultados de auditorías
- Monitorear el proceso de glosas

📊 **Reportes y Análisis:**
- Acceder a reportes de auditoría
- Interpretar resultados y estadísticas
- Analizar tendencias de glosas

📋 **Gestión de Cartera:**
- Calcular cartera actual
- Proyectar pagos futuros
- Analizar impacto de glosas

💼 **Toma de Decisiones:**
- Basar decisiones en datos de auditoría
- Optimizar procesos de pago
- Gestionar relaciones con IPS

¿En qué puedo ayudarte hoy? Puedes preguntarme sobre cualquier aspecto de la gestión de facturas y auditorías."""

        return "¡Hola! 👋 Soy tu asistente virtual para el sistema de auditoría de cuentas médicas. ¿En qué puedo ayudarte hoy?"


# Instancia global del servicio
chatbot_service = OpenRouterChatbotService() 