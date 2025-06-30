from django.db import models
from facturacion.models import Factura
from accounts.models import Profile
from accounts.models import Profile
class CuentaCartera(models.Model):
    factura = models.OneToOneField(Factura, on_delete=models.CASCADE)
    ips = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='cuentas_ips')
    eps = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='cuentas_eps')
    valor_inicial = models.DecimalField(max_digits=12, decimal_places=2)
    valor_glosado = models.DecimalField(max_digits=12, decimal_places=2)
    valor_final = models.DecimalField(max_digits=12, decimal_places=2)
    estado_pago = models.CharField(max_length=20, default="Pendiente")
