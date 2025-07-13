from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Glosa, HistorialGlosa
from decimal import Decimal

@receiver(post_save, sender=Glosa)
def manejar_respuesta_glosa(sender, instance, created, **kwargs):
    """
    Maneja el flujo automático cuando una IPS acepta una glosa
    """
    if not created and instance.estado == 'Respondida IPS' and instance.aceptada is True:
        # La IPS acepta la glosa, automáticamente finalizar el proceso
        estado_anterior = instance.estado
        
        # Cambiar estado a Aceptada ET automáticamente
        instance.estado = 'Aceptada ET'
        instance.fecha_decision_et = timezone.now().date()
        instance.valor_aceptado_et = instance.valor_glosado  # La glosa es válida, se descuenta del valor bruto
        instance.decision_et_justificacion = "Glosa aceptada automáticamente por la IPS"
        
        # Evitar bucle infinito de signals
        Glosa.objects.filter(id=instance.id).update(  # type: ignore
            estado='Aceptada ET',
            fecha_decision_et=timezone.now().date(),
            valor_aceptado_et=instance.valor_glosado,
            decision_et_justificacion="Glosa aceptada automáticamente por la IPS"
        )
        
        # Crear historial de la acción automática
        HistorialGlosa.objects.create(  # type: ignore
            glosa=instance,
            usuario=None,  # Acción automática del sistema
            accion='decidida_et',
            estado_anterior=estado_anterior,
            estado_nuevo='Aceptada ET',
            valor_anterior=instance.valor_aceptado_et,
            valor_nuevo=instance.valor_glosado,
            descripcion_cambio="Glosa aceptada automáticamente por la IPS. Glosa válida, se descuenta del valor bruto.",
        )
        
        # Actualizar la cuenta de cartera
        try:
            cuenta_cartera = instance.factura.cuentacartera
            cuenta_cartera.actualizar_valores_glosas()
        except:
            # Si no existe cuenta de cartera, crear una básica
            from cartera.models import CuentaCartera
            CuentaCartera.objects.get_or_create(  # type: ignore
                factura=instance.factura,
                defaults={
                    'ips': instance.factura.ips,
                    'eps': instance.factura.eps,
                    'valor_inicial': instance.factura.valor_bruto,
                    'valor_glosado_provisional': Decimal('0'),
                    'valor_glosado_definitivo': Decimal('0'),
                    'valor_pagable': instance.factura.valor_bruto,
                    'estado_pago': 'Pendiente'
                }
            )
            cuenta_cartera = instance.factura.cuentacartera
            cuenta_cartera.actualizar_valores_glosas()

@receiver(post_save, sender=Glosa)
def actualizar_cartera_glosa(sender, instance, created, **kwargs):
    """
    Actualiza la cuenta de cartera cuando se crea o modifica una glosa
    """
    try:
        cuenta_cartera = instance.factura.cuentacartera
        cuenta_cartera.actualizar_valores_glosas()
    except:
        # Si no existe cuenta de cartera, no hacer nada
        pass 