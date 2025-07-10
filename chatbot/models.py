from django.db import models
from django.contrib.auth.models import User
from accounts.models import Profile


class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    role = models.CharField(max_length=20, choices=[
        ('IPS', 'IPS'),
        ('ET', 'Entidad Territorial'),
        ('AUDITOR', 'Auditor'),
        ('EPS', 'EPS'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat de {self.user.username} - {self.role}"


class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_user_message = models.BooleanField(default=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message in {self.session} at {self.timestamp}"
