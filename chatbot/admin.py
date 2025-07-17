from django.contrib import admin
from .models import ChatSession, ChatMessage
from import_export import resources
from import_export.admin import ImportExportModelAdmin


# Recursos para import-export
class ChatSessionResource(resources.ModelResource):
    class Meta:
        model = ChatSession
        import_id_fields = ('id',)
        export_order = ('user', 'role', 'created_at', 'updated_at', 'is_active')


class ChatMessageResource(resources.ModelResource):
    class Meta:
        model = ChatMessage
        import_id_fields = ('id',)
        export_order = ('session', 'message', 'response', 'timestamp', 'is_user_message')


# Admin classes con import-export
@admin.register(ChatSession)
class ChatSessionAdmin(ImportExportModelAdmin):
    resource_class = ChatSessionResource
    list_display = ('user', 'role', 'created_at', 'updated_at', 'is_active')
    list_filter = ('role', 'is_active', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'role')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)


@admin.register(ChatMessage)
class ChatMessageAdmin(ImportExportModelAdmin):
    resource_class = ChatMessageResource
    list_display = ('session', 'is_user_message', 'timestamp', 'message_preview', 'response_preview')
    list_filter = ('is_user_message', 'timestamp', 'session__role')
    search_fields = ('session__user__username', 'message', 'response')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    
    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Mensaje'
    
    def response_preview(self, obj):
        return obj.response[:100] + '...' if len(obj.response) > 100 else obj.response
    response_preview.short_description = 'Respuesta'
