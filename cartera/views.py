from django.shortcuts import render
from .models import CuentaCartera
from decimal import Decimal


def resumen_cartera(request):
    # Obtener todas las cuentas de cartera
    cuentas = CuentaCartera.objects.select_related('factura', 'ips', 'eps').all()
    
    # Calcular totales
    valor_inicial_total = sum(cuenta.valor_inicial or Decimal('0') for cuenta in cuentas)
    glosas_provisionales_total = sum(cuenta.valor_glosado_provisional or Decimal('0') for cuenta in cuentas)
    glosas_definitivas_total = sum(cuenta.valor_glosado_definitivo or Decimal('0') for cuenta in cuentas)
    valor_pagable_total = sum(cuenta.valor_pagable or Decimal('0') for cuenta in cuentas)
    
    return render(request, 'cartera/resumen_cartera.html', {
        'cuentas': cuentas,
        'valor_inicial_total': valor_inicial_total,
        'glosas_provisionales_total': glosas_provisionales_total,
        'glosas_definitivas_total': glosas_definitivas_total,
        'valor_pagable_total': valor_pagable_total,
    })
