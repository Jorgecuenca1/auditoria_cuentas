from django.db import models
from facturacion.models import Factura
from accounts.models import Profile
from decimal import Decimal

class CuentaCartera(models.Model):
    ESTADO_PAGO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Parcialmente_Glosado', 'Parcialmente Glosado'),
        ('Glosas_Pendientes', 'Glosas Pendientes'),
        ('Finalizado', 'Finalizado'),
        ('Pagado', 'Pagado'),
    ]
    
    factura = models.OneToOneField(Factura, on_delete=models.CASCADE)
    ips = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='cuentas_ips')
    eps = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='cuentas_eps')
    
    # Valores financieros
    valor_inicial = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        help_text="Valor bruto inicial de la factura"
    )
    valor_glosado = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0, 
        help_text="[LEGACY] Valor glosado total"
    )
    valor_final = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True,
        blank=True,
        help_text="[LEGACY] Valor final"
    )
    
    # Nuevos campos para gestión automática
    valor_glosado_provisional = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0, 
        null=True, 
        blank=True,
        help_text="Valor total de glosas pendientes/en proceso"
    )
    valor_glosado_definitivo = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0, 
        null=True, 
        blank=True,
        help_text="Valor total de glosas aceptadas definitivamente"
    )
    valor_pagable = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Valor final a pagar (inicial - glosado_definitivo)"
    )
    
    # Estado y fechas
    estado_pago = models.CharField(
        max_length=20, 
        choices=ESTADO_PAGO_CHOICES, 
        default="Pendiente"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, 
        null=True
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True, 
        null=True
    )

    def save(self, *args, **kwargs):
        """Actualiza automáticamente valor_pagable y valor_final cuando se guarda"""
        if self.valor_glosado_definitivo is not None:
            self.valor_pagable = self.valor_inicial - self.valor_glosado_definitivo
        else:
            self.valor_pagable = self.valor_inicial
        
        # Calcular valor_final legacy (debe ser igual a valor_pagable)
        if self.valor_pagable is not None:
            self.valor_final = self.valor_pagable
        else:
            self.valor_final = self.valor_inicial
            
        super().save(*args, **kwargs)

    def actualizar_valores_glosas(self):
        """Recalcula los valores de glosas basado en las glosas asociadas"""
        from auditoria.models import Glosa
        
        glosas = Glosa.objects.filter(factura=self.factura)
        
        # Calcular glosas provisionales (pendientes o en proceso)
        glosas_provisionales = glosas.filter(
            estado__in=['Pendiente', 'Respondida IPS', 'Devuelta a IPS']
        )
        self.valor_glosado_provisional = sum(g.valor_glosado for g in glosas_provisionales) or Decimal('0')
        
        # Calcular glosas definitivas (aceptadas por ET = se descuentan del valor bruto)
        glosas_definitivas = glosas.filter(estado='Rechazada ET')  # Rechazada ET = glosa válida, se descuenta
        self.valor_glosado_definitivo = sum(g.valor_aceptado_et or g.valor_glosado for g in glosas_definitivas) or Decimal('0')
        
        # Actualizar valor pagable
        self.valor_pagable = self.valor_inicial - self.valor_glosado_definitivo
        
        # Calcular valor_final legacy (debe ser igual a valor_pagable)
        self.valor_final = self.valor_pagable
        
        # Actualizar estado según los valores
        if self.valor_glosado_definitivo > 0 and self.valor_glosado_provisional > 0:
            self.estado_pago = 'Parcialmente_Glosado'
        elif self.valor_glosado_provisional > 0:
            self.estado_pago = 'Glosas_Pendientes'
        elif self.valor_glosado_definitivo > 0:
            self.estado_pago = 'Finalizado'
        else:
            self.estado_pago = 'Pendiente'
        
        self.save()

    def __str__(self):
        return f"Cartera {self.factura.numero} - {self.ips.name}"

    class Meta:
        verbose_name = "Cuenta de Cartera"
        verbose_name_plural = "Cuentas de Cartera"
