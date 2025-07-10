from django.contrib import admin
from .models import ChatSession, ChatMessage


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'role', 'created_at', 'updated_at', 'is_active', 'message_count']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Mensajes'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'is_user_message', 'message_preview', 'response_preview', 'timestamp']
    list_filter = ['is_user_message', 'timestamp', 'session__role']
    search_fields = ['message', 'response', 'session__user__username']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def message_preview(self, obj):
        if obj.is_user_message:
            return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
        return '-'
    message_preview.short_description = 'Mensaje'
    
    def response_preview(self, obj):
        if not obj.is_user_message:
            return obj.response[:50] + '...' if len(obj.response) > 50 else obj.response
        return '-'
    response_preview.short_description = 'Respuesta'
