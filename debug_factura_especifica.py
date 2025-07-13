#!/usr/bin/env python
import os
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auditoria_cuentas.settings')
django.setup()

from facturacion.models import *
from facturacion.validators import validate_rips_item

def debug_factura_especifica():
    """Debug por qué no se guardaron los RIPS para la factura HDVE1158066"""
    
    print("=== DEBUG FACTURA ESPECÍFICA ===")
    
    # Buscar la factura
    try:
        factura = Factura.objects.get(numero='HDVE1158066')
        print(f"✓ Factura encontrada: {factura.numero}")
        print(f"  - Fecha radicación: {factura.fecha_radicacion}")
        print(f"  - Valor bruto: ${factura.valor_bruto:,.2f}")
        print(f"  - Estado: {factura.estado}")
        print(f"  - Paciente: {factura.paciente}")
        
        # Verificar RIPS asociados
        consultas = RipsConsulta.objects.filter(factura=factura).count()
        medicamentos = RipsMedicamento.objects.filter(factura=factura).count()
        procedimientos = RipsProcedimiento.objects.filter(factura=factura).count()
        hospitalizaciones = RipsHospitalizacion.objects.filter(factura=factura).count()
        otros = RipsOtroServicio.objects.filter(factura=factura).count()
        
        print(f"\n=== RIPS ASOCIADOS ===")
        print(f"Consultas: {consultas}")
        print(f"Medicamentos: {medicamentos}")
        print(f"Procedimientos: {procedimientos}")
        print(f"Hospitalizaciones: {hospitalizaciones}")
        print(f"Otros servicios: {otros}")
        
        total_items = consultas + medicamentos + procedimientos + hospitalizaciones + otros
        print(f"TOTAL ITEMS: {total_items}")
        
        # Cargar el archivo RIPS original
        rips_file = "rips/Rips_HDVE1158066.json"
        print(f"\n=== ANÁLISIS DEL ARCHIVO RIPS ===")
        
        with open(rips_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Contar items esperados
        total_esperado = 0
        for user_data in data.get("usuarios", []):
            servicios = user_data.get("servicios", {})
            for service_type, items_list in servicios.items():
                count = len(items_list)
                total_esperado += count
                print(f"{service_type}: {count} items")
        
        print(f"TOTAL ESPERADO: {total_esperado}")
        print(f"TOTAL GUARDADO: {total_items}")
        print(f"DIFERENCIA: {total_esperado - total_items}")
        
        # Verificar si hay problemas de validación
        print(f"\n=== SIMULACIÓN DE VALIDACIÓN ===")
        items_validos = 0
        items_invalidos = 0
        
        for user_data in data.get("usuarios", []):
            servicios = user_data.get("servicios", {})
            for service_type, items_list in servicios.items():
                for item_data in items_list:
                    try:
                        validation_errors = validate_rips_item(item_data, service_type)
                        if validation_errors:
                            items_invalidos += 1
                        else:
                            items_validos += 1
                    except Exception as e:
                        items_invalidos += 1
                        print(f"Error validando {service_type}: {e}")
        
        print(f"Items válidos: {items_validos}")
        print(f"Items inválidos: {items_invalidos}")
        
        # Verificar si el problema es que no se están guardando items inválidos
        if items_validos == total_items:
            print("✓ Solo se guardaron los items válidos")
        elif total_items == 0:
            print("❌ NO SE GUARDÓ NINGÚN ITEM - Posible error en el proceso")
        else:
            print("⚠️  Hay una discrepancia en el guardado")
            
        # Verificar otras facturas con el mismo número
        facturas_similares = Factura.objects.filter(numero__icontains='HDVE1158066')
        print(f"\n=== FACTURAS SIMILARES ===")
        for f in facturas_similares:
            print(f"  - {f.numero} (ID: {f.id}, Fecha: {f.fecha_radicacion})")
            c = RipsConsulta.objects.filter(factura=f).count()
            m = RipsMedicamento.objects.filter(factura=f).count()
            p = RipsProcedimiento.objects.filter(factura=f).count()
            h = RipsHospitalizacion.objects.filter(factura=f).count()
            o = RipsOtroServicio.objects.filter(factura=f).count()
            print(f"    RIPS: C={c}, M={m}, P={p}, H={h}, O={o}")
        
    except Factura.DoesNotExist:
        print("❌ Factura HDVE1158066 no encontrada")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_factura_especifica() 