#!/usr/bin/env python3
import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auditoria_cuentas.settings')
django.setup()

from facturacion.models import Factura, SubcodigoDevolucion, Devolucion
from accounts.models import Profile

def test_validacion_22_dias():
    """Prueba la validación de 22 días para facturas"""
    
    print("=== PRUEBA DE VALIDACIÓN DE 22 DÍAS ===")
    
    # Verificar que existe el código DE5601
    try:
        subcodigo = SubcodigoDevolucion.objects.get(subcodigo='DE5601')
        print(f"✓ Código DE5601 encontrado: {subcodigo.descripcion}")
    except SubcodigoDevolucion.DoesNotExist:
        print("✗ Error: Código DE5601 no encontrado")
        return
    
    # Verificar facturas existentes
    facturas_totales = Factura.objects.count()
    print(f"📊 Total de facturas en el sistema: {facturas_totales}")
    
    # Buscar facturas con más de 22 días
    fecha_limite = date.today() - timedelta(days=22)
    facturas_antiguas = Factura.objects.filter(fecha_emision__lt=fecha_limite)
    
    print(f"📅 Facturas con fecha de emisión anterior a {fecha_limite}:")
    for factura in facturas_antiguas:
        dias_transcurridos = (date.today() - factura.fecha_emision).days
        print(f"  - Factura {factura.numero}: {factura.fecha_emision} ({dias_transcurridos} días)")
        
        # Verificar si ya fue devuelta por este motivo
        devolucion_22_dias = Devolucion.objects.filter(
            factura=factura,
            subcodigo__subcodigo='DE5601'
        ).first()
        
        if devolucion_22_dias:
            print(f"    ✓ Ya devuelta por 22 días: {devolucion_22_dias.justificacion}")
        else:
            print(f"    ⚠️  No devuelta por 22 días (estado: {factura.estado})")
    
    # Mostrar estadísticas
    facturas_devueltas_22_dias = Devolucion.objects.filter(subcodigo__subcodigo='DE5601').count()
    print(f"\n📊 Estadísticas:")
    print(f"  - Facturas con más de 22 días: {facturas_antiguas.count()}")
    print(f"  - Facturas devueltas por 22 días: {facturas_devueltas_22_dias}")
    
    # Mostrar ejemplo de cálculo
    print(f"\n📋 Ejemplo de cálculo:")
    print(f"  - Fecha actual: {date.today()}")
    print(f"  - Fecha límite (22 días atrás): {fecha_limite}")
    print(f"  - Una factura del {fecha_limite - timedelta(days=1)} tendría {(date.today() - (fecha_limite - timedelta(days=1))).days} días")

if __name__ == "__main__":
    test_validacion_22_dias() 