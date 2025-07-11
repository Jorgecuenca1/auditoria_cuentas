try:
    import google.generativeai as genai
    # Verificar si GenerativeModel está disponible
    if hasattr(genai, 'GenerativeModel'):
        GEMINI_AVAILABLE = True
        print("Google Generative AI disponible con GenerativeModel")
    else:
        GEMINI_AVAILABLE = False
        print("Google Generative AI disponible pero sin GenerativeModel")
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai no está disponible")

from django.conf import settings
from typing import List, Dict, Optional
import json


class GeminiChatbotService:
    def __init__(self):
        self.model = None
        
        if not GEMINI_AVAILABLE:
            print("Error: google-generativeai no está disponible")
            return
            
        try:
            # Intentar diferentes métodos de configuración
            if hasattr(genai, 'configure'):
                genai.configure(api_key=settings.GEMINI_API_KEY)
                print("Gemini configurado correctamente")
            else:
                print("Error: genai.configure no está disponible")
                return
                
            if hasattr(genai, 'GenerativeModel'):
                self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
                print(f"Modelo Gemini creado: {settings.GEMINI_MODEL}")
            else:
                print("Error: GenerativeModel no está disponible en esta versión")
                return
                
        except Exception as e:
            print(f"Error configurando Gemini: {str(e)}")
            self.model = None
        
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
        Genera una respuesta usando Gemini basada en el rol del usuario y el historial de conversación
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
        prompt = f"""
        {context}
        
        {history_context}
        
        Pregunta del usuario: {message}
        
        Responde de manera útil, clara y específica para el rol de {role}. 
        Si la pregunta no está relacionada con el sistema de auditoría de cuentas médicas, 
        indícalo amablemente y sugiere hacer preguntas relacionadas con el sistema.
        """
        
        # Verificar si el modelo está disponible
        if not self.model:
            print("Error en Servicio Gemini: Modelo no disponible")
        else:
            try:
                # Generar respuesta con Gemini
                print(f"Enviando prompt a Gemini: {prompt[:200]}...")
                response = self.model.generate_content(prompt)
                print(f"Respuesta de Gemini: {response.text[:200]}...")
                return response.text
            except Exception as e:
                print(f"Error en Gemini: {str(e)}")
        
        # Si llegamos aquí, usar respuestas de fallback
        # Respuestas de fallback específicas por rol
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
   - **Respuesta**: Explica detalladamente por qué no estás de acuerdo con la glosa
   - **Documentos**: Sube evidencia que respalde tu respuesta (opcional)
   - **Justificación**: Incluye fundamentos técnicos o normativos

4. **Enviar:**
   - Revisa que toda la información esté completa
   - Haz clic en "Enviar Respuesta"

5. **Seguimiento:**
   - La ET revisará tu respuesta y tomará una decisión
   - Puedes ver el estado en el historial de la glosa

**Consejos:**
- Sé específico y técnico en tu respuesta
- Incluye referencias normativas cuando sea posible
- Adjunta documentos que respalden tu posición
- Responde dentro del plazo establecido

¿Necesitas ayuda con algún paso específico?"""
            else:
                return """¡Hola! Soy tu asistente para el sistema de auditoría de cuentas médicas.

Como IPS, puedo ayudarte con:
• **Responder glosas** y subir documentos de soporte
• **Ver el estado** de tus facturas y glosas  
• **Acceder al historial** de tus glosas
• **Manejar devoluciones** de facturas
• **Generar reportes** específicos de tu IPS

¿Qué te gustaría saber? Puedes preguntarme sobre:
- "¿Cómo respondo una glosa?"
- "¿Dónde veo el manual de usuario?"
- "¿Cómo subo documentos de soporte?"
- "¿Cómo veo el historial de mis glosas?" """
        else:
            return "Lo siento, estoy teniendo problemas técnicos. Por favor intenta de nuevo."

    def get_welcome_message(self, role: str) -> str:
        """
        Genera un mensaje de bienvenida personalizado para cada rol
        """
        welcome_messages = {
            'IPS': """
            ¡Hola! Soy tu asistente virtual especializado en el sistema de auditoría de cuentas médicas para IPS.
            
            Puedo ayudarte con:
            • Responder glosas y subir documentos de soporte
            • Ver el estado de tus facturas y glosas
            • Interpretar decisiones de la ET
            • Acceder al historial de tus glosas
            • Manejar devoluciones de facturas
            
            ¿En qué puedo ayudarte hoy?
            """,
            'ET': """
            ¡Hola! Soy tu asistente virtual especializado en el sistema de auditoría de cuentas médicas para Entidades Territoriales.
            
            Puedo ayudarte con:
            • Crear y gestionar glosas
            • Decidir sobre respuestas de IPS
            • Generar reportes de auditoría
            • Devolver facturas cuando sea necesario
            • Analizar el historial completo de glosas
            
            ¿En qué puedo ayudarte hoy?
            """,
            'AUDITOR': """
            ¡Hola! Soy tu asistente virtual especializado en el sistema de auditoría de cuentas médicas para auditores.
            
            Puedo ayudarte con:
            • Realizar auditorías completas
            • Revisar glosas y su historial
            • Generar reportes detallados
            • Finalizar auditorías
            • Analizar datos de auditoría
            
            ¿En qué puedo ayudarte hoy?
            """,
            'EPS': """
            ¡Hola! Soy tu asistente virtual especializado en el sistema de auditoría de cuentas médicas para EPS.
            
            Puedo ayudarte con:
            • Revisar el estado de facturas
            • Acceder a reportes de auditoría
            • Interpretar resultados de auditoría
            • Ver el historial de glosas
            • Gestionar cartera y pagos
            
            ¿En qué puedo ayudarte hoy?
            """
        }
        
        return welcome_messages.get(role, "¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte?") 