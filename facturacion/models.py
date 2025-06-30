from django.db import models
from accounts.models import Profile
class Factura(models.Model):
    numero = models.CharField(max_length=50)
    cufe = models.CharField(max_length=150)
    fecha_emision = models.DateField()
    fecha_radicacion = models.DateField(auto_now_add=True)
    ips = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='facturas_ips')
    eps = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='facturas_eps')
    valor_bruto = models.DecimalField(max_digits=12, decimal_places=2)
    estado_auditoria = models.CharField(max_length=20, default="Radicada")
    archivo_rips = models.FileField(upload_to='rips/')

    def __str__(self):
        return f"Factura {self.numero} CUFE {self.cufe}"

class RipsItem(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    tipo_servicio = models.CharField(max_length=50)
    paciente_id = models.CharField(max_length=50)
    codigo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255, blank=True)
    fecha = models.CharField(max_length=50)
    diagnostico = models.CharField(max_length=50)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    cod_prestador = models.CharField(max_length=50, blank=True, null=True)
