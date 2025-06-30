from django.shortcuts import render
from facturacion.models import Factura


def resumen_cartera(request):
    facturas = Factura.objects.filter(estado_auditoria="Cerrada")
    return render(request, 'cartera/resumen_cartera.html', {'facturas': facturas})
