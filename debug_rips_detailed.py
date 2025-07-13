#!/usr/bin/env python
import os
import sys
import django
import json
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auditoria_cuentas.settings')
django.setup()

from facturacion.models import *
from facturacion.validators import validate_rips_item
from facturacion.views import parse_date_time

def debug_rips_processing():
    """Debug detallado del procesamiento de RIPS"""
    
    # Cargar archivo RIPS
    rips_file = "rips/Rips_HDVE1158066.json"
    
    print("=== DEBUG RIPS PROCESSING ===")
    print(f"Archivo: {rips_file}")
    
    try:
        with open(rips_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✓ Archivo cargado correctamente")
        print(f"Usuarios en RIPS: {len(data.get('usuarios', []))}")
        
        # Verificar estructura
        for i, user_data in enumerate(data.get("usuarios", [])):
            print(f"\n--- Usuario {i+1} ---")
            servicios = user_data.get("servicios", {})
            print(f"Servicios disponibles: {list(servicios.keys())}")
            
            for service_type, items_list in servicios.items():
                print(f"\n{service_type.upper()}: {len(items_list)} items")
                
                for j, item_data in enumerate(items_list):
                    print(f"\n  Item {j+1}/{len(items_list)} ({service_type}):")
                    print(f"    Consecutivo: {item_data.get('consecutivo')}")
                    print(f"    Valor servicio: {item_data.get('vrServicio')}")
                    
                    # Validar item
                    print(f"    Validando item...")
                    try:
                        validation_errors = validate_rips_item(item_data, service_type)
                        if validation_errors:
                            print(f"    ❌ Errores de validación: {validation_errors}")
                        else:
                            print(f"    ✓ Validación exitosa")
                    except Exception as e:
                        print(f"    ❌ Error en validación: {e}")
                        continue
                    
                    # Simular creación de common_fields
                    try:
                        common_fields = {
                            'factura': None,  # Simular
                            'paciente': None,  # Simular
                            'cod_prestador': item_data.get("codPrestador", ""),
                            'num_autorizacion': item_data.get("numAutorizacion", ""),
                            'vr_servicio': item_data.get("vrServicio", 0) if item_data.get("vrServicio") is not None else 0,
                            'concepto_recaudo': item_data.get("conceptoRecaudo", ""),
                            'valor_pago_moderador': item_data.get("valorPagoModerador", 0) if item_data.get("valorPagoModerador") is not None else 0,
                            'consecutivo': item_data.get("consecutivo", 0) if item_data.get("consecutivo") is not None else 0,
                        }
                        print(f"    ✓ Common fields creados")
                        
                        # Verificar campos específicos por tipo
                        if service_type == "consultas":
                            fecha_inicio = parse_date_time(item_data.get("fechaInicioAtencion"))
                            print(f"    Fecha inicio: {fecha_inicio}")
                            print(f"    Cod consulta: {item_data.get('codConsulta')}")
                            
                        elif service_type == "medicamentos":
                            fecha_disp = parse_date_time(item_data.get("fechaDispensAdmon"))
                            print(f"    Fecha dispensación: {fecha_disp}")
                            print(f"    Cod tecnología: {item_data.get('codTecnologiaSalud')}")
                            
                        elif service_type == "procedimientos":
                            fecha_inicio = parse_date_time(item_data.get("fechaInicioAtencion"))
                            print(f"    Fecha inicio: {fecha_inicio}")
                            print(f"    Cod procedimiento: {item_data.get('codProcedimiento')}")
                            
                        elif service_type == "hospitalizacion":
                            fecha_ingreso = parse_date_time(item_data.get("fechaIngresoHospitalizacion"))
                            print(f"    Fecha ingreso: {fecha_ingreso}")
                            print(f"    Via ingreso: {item_data.get('viaIngresoServicioSalud')}")
                            
                        elif service_type == "otrosServicios":
                            fecha_suministro = parse_date_time(item_data.get("fechaSuministroTecnologia"))
                            print(f"    Fecha suministro: {fecha_suministro}")
                            print(f"    Tipo OS: {item_data.get('tipoOS')}")
                            
                        print(f"    ✓ Campos específicos procesados")
                        
                    except Exception as e:
                        print(f"    ❌ Error procesando item: {e}")
                        import traceback
                        traceback.print_exc()
                        
        # Verificar modelos existentes
        print(f"\n=== ESTADO ACTUAL DE LA BD ===")
        print(f"Facturas: {Factura.objects.count()}")
        print(f"RipsConsulta: {RipsConsulta.objects.count()}")
        print(f"RipsMedicamento: {RipsMedicamento.objects.count()}")
        print(f"RipsProcedimiento: {RipsProcedimiento.objects.count()}")
        print(f"RipsHospitalizacion: {RipsHospitalizacion.objects.count()}")
        print(f"RipsOtroServicio: {RipsOtroServicio.objects.count()}")
        
        # Verificar si hay facturas recientes
        facturas_recientes = Factura.objects.order_by('-fecha_creacion')[:3]
        print(f"\nFacturas recientes:")
        for f in facturas_recientes:
            print(f"  - {f.numero_factura} (Lote: {f.lote}, Fecha: {f.fecha_creacion})")
            
            # Verificar RIPS asociados
            consultas = RipsConsulta.objects.filter(factura=f).count()
            medicamentos = RipsMedicamento.objects.filter(factura=f).count()
            procedimientos = RipsProcedimiento.objects.filter(factura=f).count()
            hospitalizacion = RipsHospitalizacion.objects.filter(factura=f).count()
            otros = RipsOtroServicio.objects.filter(factura=f).count()
            
            print(f"    RIPS: C={consultas}, M={medicamentos}, P={procedimientos}, H={hospitalizacion}, O={otros}")
                        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_rips_processing() 