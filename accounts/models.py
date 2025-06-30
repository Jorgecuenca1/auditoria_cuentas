from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = (
        ('IPS', 'IPS'),
        ('EPS', 'EPS'),
        ('ET', 'Entidad Territorial'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    entidad_nombre = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
