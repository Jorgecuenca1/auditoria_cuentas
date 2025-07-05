from django.shortcuts import render
from facturacion.models import Factura


def resumen_cartera(request):
    facturas = Factura.objects.filter(estado="Auditada")
    total_cartera = sum(f.valor_bruto for f in facturas)
    return render(request, 'cartera/resumen_cartera.html', {
        'facturas': facturas,
        'total_cartera': total_cartera
    })
