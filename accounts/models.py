from django.db import models
from django.contrib.auth.models import User

class CatalogoCUPS(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

class CatalogoCIE10(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    descripcion = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

class CatalogoCUMS(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

class CatalogoMunicipio(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=255)
    def __str__(self):
        return self.nombre

class CatalogoPais(models.Model):
    codigo = models.CharField(max_length=5, unique=True)
    nombre = models.CharField(max_length=255)
    def __str__(self):
        return self.nombre

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = (
        ('IPS', 'IPS'),
        ('EPS', 'EPS'),
        ('ET', 'Entidad Territorial'),
        ('ADMIN', 'Administrador'),
        ('AUDITOR', 'Auditor'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    entidad_nombre = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return f"{self.user.username} ({self.role})"
