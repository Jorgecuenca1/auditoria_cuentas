from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from accounts.decorators import role_required
from .models import ChatSession, ChatMessage
from .services import GeminiChatbotService
import json


@login_required
def chatbot_view(request):
    """
    Vista principal del chatbot
    """
    user_role = request.user.profile.role
    
    # Obtener o crear sesión de chat activa
    session, created = ChatSession.objects.get_or_create(
        user=request.user,
        role=user_role,
        is_active=True,
        defaults={'is_active': True}
    )
    
    # Si se creó una nueva sesión, enviar mensaje de bienvenida
    if created:
        chatbot_service = GeminiChatbotService()
        welcome_message = chatbot_service.get_welcome_message(user_role)
        
        # Crear mensaje de bienvenida
        ChatMessage.objects.create(
            session=session,
            message="",
            response=welcome_message,
            is_user_message=False
        )
    
    # Obtener mensajes de la sesión
    messages = session.messages.all()
    
    context = {
        'session': session,
        'messages': messages,
        'user_role': user_role,
    }
    
    return render(request, 'chatbot/chatbot.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """
    Vista para enviar mensajes al chatbot
    """
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({'error': 'El mensaje no puede estar vacío'}, status=400)
        
        user_role = request.user.profile.role
        
        # Obtener sesión activa
        try:
            session = ChatSession.objects.get(user=request.user, role=user_role, is_active=True)
        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Sesión de chat no encontrada'}, status=404)
        
        # Obtener historial de conversación
        conversation_history = []
        messages = session.messages.all().order_by('-timestamp')[:10]  # Últimos 10 mensajes
        for msg in reversed(messages):  # Revertir para orden cronológico
            conversation_history.append({
                'message': msg.message,
                'response': msg.response,
                'is_user_message': msg.is_user_message
            })
        
        # Generar respuesta con Gemini
        try:
            chatbot_service = GeminiChatbotService()
            response = chatbot_service.get_response(message, user_role, conversation_history)
        except Exception as e:
            print(f"Error en Gemini service: {str(e)}")
            response = "Lo siento, estoy teniendo problemas técnicos en este momento. Por favor intenta de nuevo en unos minutos."
        
        # Guardar mensaje del usuario
        user_message = ChatMessage.objects.create(
            session=session,
            message=message,
            response="",
            is_user_message=True
        )
        
        # Guardar respuesta del bot
        bot_message = ChatMessage.objects.create(
            session=session,
            message="",
            response=response,
            is_user_message=False
        )
        
        # Actualizar timestamp de la sesión
        session.save()
        
        return JsonResponse({
            'success': True,
            'response': response,
            'user_message_id': user_message.id,
            'bot_message_id': bot_message.id,
            'timestamp': bot_message.timestamp.isoformat()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        print(f"Error en send_message: {str(e)}")
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)


@login_required
def chat_history(request):
    """
    Vista para ver el historial de chats
    """
    user_role = request.user.profile.role
    sessions = ChatSession.objects.filter(user=request.user, role=user_role).order_by('-updated_at')
    
    context = {
        'sessions': sessions,
        'user_role': user_role,
    }
    
    return render(request, 'chatbot/chat_history.html', context)


@login_required
def start_new_chat(request):
    """
    Vista para iniciar una nueva sesión de chat
    """
    user_role = request.user.profile.role
    
    # Desactivar sesión actual si existe
    ChatSession.objects.filter(user=request.user, role=user_role, is_active=True).update(is_active=False)
    
    # Crear nueva sesión
    session = ChatSession.objects.create(
        user=request.user,
        role=user_role,
        is_active=True
    )
    
    # Enviar mensaje de bienvenida
    chatbot_service = GeminiChatbotService()
    welcome_message = chatbot_service.get_welcome_message(user_role)
    
    ChatMessage.objects.create(
        session=session,
        message="",
        response=welcome_message,
        is_user_message=False
    )
    
    return redirect('chatbot:chatbot_view')


@login_required
def load_chat_session(request, session_id):
    """
    Vista para cargar una sesión de chat específica
    """
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
        
        # Desactivar sesión actual
        ChatSession.objects.filter(user=request.user, role=session.role, is_active=True).update(is_active=False)
        
        # Activar la sesión seleccionada
        session.is_active = True
        session.save()
        
        return redirect('chatbot:chatbot_view')
        
    except ChatSession.DoesNotExist:
        return redirect('chatbot:chatbot_view')
