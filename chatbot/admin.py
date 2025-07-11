from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import ChatSession, ChatMessage

# Resources para import/export
class ChatSessionResource(resources.ModelResource):
    class Meta:
        model = ChatSession
        import_id_fields = ('id',)
        fields = ('id', 'user', 'role', 'created_at', 'updated_at', 'is_active')

class ChatMessageResource(resources.ModelResource):
    class Meta:
        model = ChatMessage
        import_id_fields = ('id',)
        fields = ('id', 'session', 'is_user_message', 'message', 'response', 'timestamp')

@admin.register(ChatSession)
class ChatSessionAdmin(ImportExportModelAdmin):
    resource_class = ChatSessionResource
    list_display = ['id', 'user', 'role', 'created_at', 'updated_at', 'is_active', 'message_count']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Mensajes'


@admin.register(ChatMessage)
class ChatMessageAdmin(ImportExportModelAdmin):
    resource_class = ChatMessageResource
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
