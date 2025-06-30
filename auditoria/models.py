from django.db import models
from facturacion.models import Factura, RipsItem
from accounts.models import Profile

class Glosa(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    item = models.ForeignKey(RipsItem, on_delete=models.SET_NULL, null=True, blank=True)
    codigo_glosa = models.CharField(max_length=20)
    descripcion = models.TextField()
    valor_glosado = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20, default="Pendiente")
    respuesta = models.TextField(blank=True)
    aceptada = models.BooleanField(null=True, blank=True)
    fecha_glosa = models.DateField(auto_now_add=True)
    fecha_respuesta = models.DateField(null=True, blank=True)
