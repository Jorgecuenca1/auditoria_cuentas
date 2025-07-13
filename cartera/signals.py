from django.db.models.signals import post_save
from django.dispatch import receiver
from facturacion.models import Factura
from .models import CuentaCartera
from decimal import Decimal

@receiver(post_save, sender=Factura)
def crear_cuenta_cartera(sender, instance, created, **kwargs):
    """
    Crea automáticamente una cuenta de cartera cuando se radica una factura
    """
    if created and instance.estado == 'Radicada':
        # Verificar que no exista ya una cuenta de cartera
        if not hasattr(instance, 'cuentacartera'):
            CuentaCartera.objects.create(  # type: ignore
                factura=instance,
                ips=instance.ips,
                eps=instance.eps,
                valor_inicial=instance.valor_bruto,
                valor_glosado_provisional=Decimal('0'),
                valor_glosado_definitivo=Decimal('0'),
                valor_pagable=instance.valor_bruto,
                estado_pago='Pendiente'
            ) 