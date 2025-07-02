from django.db import models
from facturacion.models import Factura, Paciente, RipsConsulta, RipsMedicamento, RipsProcedimiento, RipsHospitalizacion, RipsOtroServicio
from accounts.models import Profile

class Glosa(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente, on_delete=models.SET_NULL, null=True, blank=True)
    consulta = models.ForeignKey(RipsConsulta, on_delete=models.SET_NULL, null=True, blank=True)
    medicamento = models.ForeignKey(RipsMedicamento, on_delete=models.SET_NULL, null=True, blank=True)
    procedimiento = models.ForeignKey(RipsProcedimiento, on_delete=models.SET_NULL, null=True, blank=True)
    hospitalizacion = models.ForeignKey(RipsHospitalizacion, on_delete=models.SET_NULL, null=True, blank=True)
    otro_servicio = models.ForeignKey(RipsOtroServicio, on_delete=models.SET_NULL, null=True, blank=True)
    codigo_glosa = models.CharField(max_length=20)
    descripcion = models.TextField()
    valor_glosado = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20, default="Pendiente")
    respuesta = models.TextField(blank=True)
    aceptada = models.BooleanField(null=True, blank=True)
    fecha_glosa = models.DateField(auto_now_add=True)
    fecha_respuesta = models.DateField(null=True, blank=True)
