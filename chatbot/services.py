import requests
import json
from django.conf import settings
from typing import List, Dict, Optional
import re


class OpenRouterChatbotService:
    def __init__(self):
        self.api_key = "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"
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "anthropic/claude-3-haiku"  # Modelo gratuito de OpenRouter
        
        # Base de conocimiento por rol con funciones específicas
        self.role_functions = {
            'IPS': {
                'name': 'IPS (Instituciones Prestadoras de Servicios de Salud)',
                'functions': {
                    'responder_glosas': {
                        'title': '📝 Responder Glosas',
                        'description': 'Cómo responder glosas de manera efectiva',
                        'steps': [
                            '1. Ve a "Glosas" → "Glosas Pendientes"',
                            '2. Busca la glosa que quieres responder',
                            '3. Haz clic en "Responder"',
                            '4. Completa el formulario con:',
                            '   • Respuesta detallada a la glosa',
                            '   • Documentos de soporte (opcional)',
                            '   • Justificación técnica',
                            '5. Haz clic en "Enviar Respuesta"'
                        ],
                        'tips': [
                            'Sé específico y detallado en tu respuesta',
                            'Incluye referencias a normativas si aplica',
                            'Adjunta toda la documentación de soporte disponible',
                            'Responde dentro del plazo establecido'
                        ]
                    },
                    'ver_estado_facturas': {
                        'title': '📊 Ver Estado de Facturas',
                        'description': 'Cómo ver el estado actual de tus facturas',
                        'steps': [
                            '1. Ve a "Radicados" en el menú principal',
                            '2. Verás todas tus facturas con su estado actual',
                            '3. Los estados posibles son:',
                            '   • Radicada: Factura enviada a la ET',
                            '   • En Auditoría: ET está revisando',
                            '   • Con Glosas: Tiene glosas pendientes',
                            '   • Aprobada: Factura aprobada para pago',
                            '   • Devuelta: Requiere correcciones'
                        ]
                    },
                    'subir_documentos': {
                        'title': '📎 Subir Documentos de Soporte',
                        'description': 'Cómo adjuntar documentos a tus respuestas',
                        'steps': [
                            '1. Al responder una glosa, verás la sección "Documentos"',
                            '2. Haz clic en "Seleccionar archivos"',
                            '3. Formatos aceptados: PDF, JPG, PNG',
                            '4. Tamaño máximo: 10MB por archivo',
                            '5. Puedes subir múltiples archivos',
                            '6. Haz clic en "Guardar" para adjuntarlos'
                        ]
                    },
                    'historial_glosas': {
                        'title': '📋 Ver Historial de Glosas',
                        'description': 'Cómo acceder al historial completo de glosas',
                        'steps': [
                            '1. Ve a "Glosas" → "Glosas Pendientes"',
                            '2. En cada glosa verás un ícono de historial',
                            '3. Haz clic en el ícono para ver:',
                            '   • Fecha de creación de la glosa',
                            '   • Respuestas enviadas',
                            '   • Decisiones de la ET',
                            '   • Documentos adjuntos',
                            '   • Cambios de estado'
                        ]
                    },
                    'manejar_devoluciones': {
                        'title': '🔄 Manejar Devoluciones',
                        'description': 'Qué hacer cuando una factura es devuelta',
                        'steps': [
                            '1. Ve a "Devoluciones" en el menú principal',
                            '2. Revisa las razones de la devolución',
                            '3. Corrige los errores identificados',
                            '4. Sube la factura corregida',
                            '5. Adjunta documentación adicional si es necesario',
                            '6. Re-radica la factura corregida'
                        ]
                    }
                }
            },
            'ET': {
                'name': 'ET (Entidad Territorial)',
                'functions': {
                    'auditar_facturas': {
                        'title': '🔍 Auditar Facturas',
                        'description': 'Cómo realizar auditorías efectivas',
                        'steps': [
                            '1. Ve a "Auditoría" → "Radicados"',
                            '2. Busca la factura que quieres auditar',
                            '3. Haz clic en "Auditar Factura"',
                            '4. Revisa todos los servicios facturados',
                            '5. Identifica items que requieren glosa',
                            '6. Crea glosas con justificación técnica'
                        ]
                    },
                    'crear_glosas': {
                        'title': '📝 Crear Glosas',
                        'description': 'Cómo crear glosas con justificación técnica',
                        'steps': [
                            '1. En la auditoría de factura, haz clic en "Crear Glosa"',
                            '2. Selecciona el tipo de glosa:',
                            '   • Técnica: Problemas con códigos, descripciones',
                            '   • Administrativa: Documentación faltante',
                            '   • Económica: Valores no autorizados',
                            '3. Completa la justificación detallada',
                            '4. Adjunta documentos de soporte si es necesario',
                            '5. Haz clic en "Guardar Glosa"'
                        ]
                    },
                    'decidir_respuestas': {
                        'title': '⚖️ Decidir sobre Respuestas de IPS',
                        'description': 'Cómo evaluar respuestas de IPS a glosas',
                        'steps': [
                            '1. Ve a "Auditoría" → "Glosas Pendientes"',
                            '2. Busca glosas con respuestas de IPS',
                            '3. Revisa la respuesta y documentación',
                            '4. Evalúa si la justificación es válida',
                            '5. Toma decisión: Aceptar o Rechazar',
                            '6. Agrega comentarios si es necesario'
                        ]
                    },
                    'generar_reportes': {
                        'title': '📊 Generar Reportes',
                        'description': 'Cómo crear reportes de auditoría',
                        'steps': [
                            '1. Ve a "Reportes" en el menú principal',
                            '2. Selecciona el tipo de reporte:',
                            '   • Reporte de Auditoría por Lote',
                            '   • Reporte de Auditoría Detalle',
                            '   • Reporte de Glosas',
                            '3. Configura los filtros de fecha y entidad',
                            '4. Haz clic en "Generar Reporte"',
                            '5. Descarga el reporte en PDF'
                        ]
                    },
                    'devolver_facturas': {
                        'title': '🔄 Devolver Facturas',
                        'description': 'Cuándo y cómo devolver facturas',
                        'steps': [
                            '1. En la auditoría, identifica errores críticos',
                            '2. Errores que justifican devolución:',
                            '   • Documentación faltante esencial',
                            '   • Errores en datos del paciente',
                            '   • Servicios no autorizados',
                            '3. Haz clic en "Devolver Factura"',
                            '4. Especifica las razones de devolución',
                            '5. La IPS recibirá notificación'
                        ]
                    }
                }
            },
            'AUDITOR': {
                'name': 'Auditor',
                'functions': {
                    'realizar_auditoria': {
                        'title': '🔍 Realizar Auditoría Completa',
                        'description': 'Proceso completo de auditoría',
                        'steps': [
                            '1. Ve a "Auditoría" → "Radicados"',
                            '2. Selecciona la factura a auditar',
                            '3. Revisa exhaustivamente:',
                            '   • Datos del paciente',
                            '   • Servicios facturados',
                            '   • Documentación de soporte',
                            '   • Valores y códigos',
                            '4. Crea glosas según hallazgos',
                            '5. Documenta todos los hallazgos'
                        ]
                    },
                    'revisar_glosas': {
                        'title': '📋 Revisar Glosas y Respuestas',
                        'description': 'Cómo revisar glosas existentes',
                        'steps': [
                            '1. Ve a "Auditoría" → "Glosas Pendientes"',
                            '2. Revisa glosas creadas por otros auditores',
                            '3. Analiza respuestas de IPS',
                            '4. Verifica documentación adjunta',
                            '5. Toma decisiones informadas',
                            '6. Documenta justificaciones'
                        ]
                    },
                    'generar_reportes_detallados': {
                        'title': '📊 Generar Reportes Detallados',
                        'description': 'Reportes especializados de auditoría',
                        'steps': [
                            '1. Ve a "Reportes" → "Reporte de Auditoría Detalle"',
                            '2. Selecciona factura específica',
                            '3. El reporte incluye:',
                            '   • Resumen ejecutivo',
                            '   • Detalle de glosas por tipo',
                            '   • Historial completo de cambios',
                            '   • Documentos adjuntos',
                            '   • Decisiones tomadas'
                        ]
                    },
                    'analizar_historial': {
                        'title': '📈 Analizar Historial de Cambios',
                        'description': 'Cómo interpretar el historial de glosas',
                        'steps': [
                            '1. En cualquier glosa, haz clic en el ícono de historial',
                            '2. Revisa cronológicamente:',
                            '   • Fecha de creación',
                            '   • Modificaciones realizadas',
                            '   • Respuestas de IPS',
                            '   • Decisiones tomadas',
                            '   • Documentos agregados'
                        ]
                    },
                    'finalizar_auditoria': {
                        'title': '✅ Finalizar Auditoría',
                        'description': 'Cómo cerrar una auditoría correctamente',
                        'steps': [
                            '1. Verifica que todas las glosas tengan decisión',
                            '2. Revisa que la documentación esté completa',
                            '3. Genera reporte final de auditoría',
                            '4. Haz clic en "Finalizar Auditoría"',
                            '5. Confirma que todos los datos estén correctos',
                            '6. La factura pasa al siguiente estado'
                        ]
                    }
                }
            },
            'EPS': {
                'name': 'EPS (Entidades Promotoras de Salud)',
                'functions': {
                    'revisar_facturas': {
                        'title': '📋 Revisar Estado de Facturas',
                        'description': 'Cómo ver el estado de tus facturas',
                        'steps': [
                            '1. Ve a "Radicados" en el menú principal',
                            '2. Filtra por tu EPS',
                            '3. Estados disponibles:',
                            '   • Radicada: Enviada a ET',
                            '   • En Auditoría: En revisión',
                            '   • Con Glosas: Tiene observaciones',
                            '   • Aprobada: Lista para pago',
                            '   • Devuelta: Requiere corrección'
                        ]
                    },
                    'ver_resultados_auditoria': {
                        'title': '📊 Ver Resultados de Auditoría',
                        'description': 'Cómo interpretar resultados de auditoría',
                        'steps': [
                            '1. Ve a "Reportes" → "Reporte de Auditoría"',
                            '2. Selecciona factura específica',
                            '3. Revisa:',
                            '   • Total facturado vs aprobado',
                            '   • Glosas aplicadas',
                            '   • Justificaciones de la ET',
                            '   • Documentos de soporte',
                            '4. Calcula el valor a pagar'
                        ]
                    },
                    'acceder_reportes': {
                        'title': '📈 Acceder a Reportes',
                        'description': 'Reportes disponibles para EPS',
                        'steps': [
                            '1. Ve a "Reportes" en el menú principal',
                            '2. Reportes disponibles:',
                            '   • Reporte de Auditoría por Lote',
                            '   • Reporte de Auditoría Detalle',
                            '   • Reporte de Glosas',
                            '   • Reporte de Cartera',
                            '3. Configura filtros de fecha y entidad',
                            '4. Descarga en formato PDF'
                        ]
                    },
                    'interpretar_glosas': {
                        'title': '🔍 Interpretar Glosas',
                        'description': 'Cómo entender las glosas aplicadas',
                        'steps': [
                            '1. En el reporte de auditoría, revisa la sección de glosas',
                            '2. Tipos de glosas:',
                            '   • Técnica: Problemas con códigos o descripciones',
                            '   • Administrativa: Documentación faltante',
                            '   • Económica: Valores no autorizados',
                            '3. Revisa justificaciones de la ET',
                            '4. Analiza impacto en el pago'
                        ]
                    },
                    'gestionar_cartera': {
                        'title': '💰 Gestionar Cartera',
                        'description': 'Cómo calcular y gestionar tu cartera',
                        'steps': [
                            '1. Ve a "Cartera" en el menú principal',
                            '2. Revisa totales:',
                            '   • Valor inicial de facturas',
                            '   • Glosas provisionales',
                            '   • Glosas definitivas',
                            '   • Valor pagable final',
                            '3. Analiza tendencias por IPS',
                            '4. Proyecta pagos futuros'
                        ]
                    }
                }
            }
        }

    def is_greeting(self, message: str) -> bool:
        """Detecta si el mensaje es un saludo"""
        greetings = [
            'hola', 'buenos días', 'buenas tardes', 'buenas noches', 'saludos',
            'hey', 'hi', 'hello', 'buen día', 'qué tal', 'como estás',
            'ayuda', 'ayúdame', 'necesito ayuda', 'qué puedes hacer',
            'funciones', 'opciones', 'menú', 'qué haces'
        ]
        
        message_lower = message.lower().strip()
        return any(greeting in message_lower for greeting in greetings)

    def get_function_menu(self, role: str) -> str:
        """Genera el menú de funciones específicas para el rol"""
        if role not in self.role_functions:
            return "Lo siento, no tengo información específica para tu rol."
        
        role_info = self.role_functions[role]
        menu = f"""🎯 **Menú de Funciones para {role_info['name']}**

Aquí tienes las funciones principales que puedo explicarte:

"""
        
        for key, function in role_info['functions'].items():
            menu += f"**{function['title']}**\n"
            menu += f"_{function['description']}_\n\n"
        
        menu += """**¿Qué función te gustaría que te explique en detalle?**

Escribe el número o el nombre de la función que te interesa:
"""
        
        # Agregar opciones numeradas
        for i, (key, function) in enumerate(role_info['functions'].items(), 1):
            menu += f"{i}. {function['title']}\n"
        
        return menu

    def get_function_details(self, role: str, function_key: str) -> str:
        """Obtiene los detalles completos de una función específica"""
        if role not in self.role_functions:
            return "Lo siento, no tengo información para tu rol."
        
        if function_key not in self.role_functions[role]['functions']:
            return "Lo siento, no encontré esa función específica."
        
        function = self.role_functions[role]['functions'][function_key]
        
        details = f"""# {function['title']}

{function['description']}

## 📋 Pasos a seguir:

"""
        
        for step in function['steps']:
            details += f"{step}\n"
        
        if 'tips' in function:
            details += "\n## 💡 Consejos importantes:\n\n"
            for tip in function['tips']:
                details += f"• {tip}\n"
        
        details += f"""

---
¿Te gustaría que te explique otra función o tienes alguna pregunta específica sobre {function['title']}?"""
        
        return details

    def get_response(self, message: str, role: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Genera una respuesta basada en el rol del usuario y el mensaje
        """
        message_lower = message.lower().strip()
        
        # Detectar si es un saludo
        if self.is_greeting(message):
            return self.get_function_menu(role)
        
        # Detectar si está pidiendo una función específica
        if role in self.role_functions:
            role_info = self.role_functions[role]
            
            # Buscar función por número
            if message_lower.isdigit():
                num = int(message_lower)
                if 1 <= num <= len(role_info['functions']):
                    function_key = list(role_info['functions'].keys())[num - 1]
                    return self.get_function_details(role, function_key)
            
            # Buscar función por nombre
            for key, function in role_info['functions'].items():
                function_words = function['title'].lower().split()
                if any(word in message_lower for word in function_words):
                    return self.get_function_details(role, key)
        
        # Respuesta genérica si no se reconoce
        return f"""No entiendo exactamente qué necesitas. 

Como {self.role_functions.get(role, {}).get('name', 'usuario')}, puedo ayudarte con las funciones del sistema.

Escribe "hola" o "ayuda" para ver el menú completo de funciones disponibles para tu rol."""

    def get_welcome_message(self, role: str) -> str:
        """Genera un mensaje de bienvenida personalizado según el rol"""
        if role not in self.role_functions:
            return "¡Hola! 👋 Soy tu asistente virtual para el sistema de auditoría de cuentas médicas. ¿En qué puedo ayudarte hoy?"
        
        role_info = self.role_functions[role]
        
        return f"""¡Hola! 👋 Soy tu asistente virtual especializado en el sistema de auditoría de cuentas médicas.

Como **{role_info['name']}**, puedo ayudarte con todas las funciones del sistema.

**¿Qué te gustaría hacer hoy?**

Escribe "hola" o "ayuda" para ver el menú completo de funciones disponibles para tu rol, o pregúntame directamente sobre cualquier proceso que necesites."""


# Instancia global del servicio
chatbot_service = OpenRouterChatbotService() 