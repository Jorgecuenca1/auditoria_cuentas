#!/usr/bin/env python
import os
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auditoria_cuentas.settings')
django.setup()

from facturacion.models import *

def verificar_ultima_factura():
    """Verificar la última factura y sus items RIPS"""
    
    print("=== VERIFICAR ÚLTIMA FACTURA ===")
    
    # Obtener la última factura
    try:
        ultima_factura = Factura.objects.order_by('-fecha_radicacion').first()
        
        if not ultima_factura:
            print("❌ No hay facturas en la base de datos")
            return
            
        print(f"✓ Última factura encontrada:")
        print(f"  - Número: {ultima_factura.numero}")
        print(f"  - Fecha radicación: {ultima_factura.fecha_radicacion}")
        print(f"  - Paciente: {ultima_factura.paciente}")
        print(f"  - Valor bruto: ${ultima_factura.valor_bruto:,.2f}")
        print(f"  - Estado: {ultima_factura.estado}")
        
        # Verificar RIPS asociados
        print(f"\n=== RIPS ASOCIADOS A LA FACTURA {ultima_factura.numero} ===")
        
        # Consultas
        consultas = RipsConsulta.objects.filter(factura=ultima_factura)
        print(f"Consultas: {consultas.count()}")
        for i, consulta in enumerate(consultas, 1):
            print(f"  {i}. Consecutivo: {consulta.consecutivo}, Valor: ${consulta.vr_servicio:,.2f}, Código: {consulta.cod_consulta}")
        
        # Medicamentos
        medicamentos = RipsMedicamento.objects.filter(factura=ultima_factura)
        print(f"\nMedicamentos: {medicamentos.count()}")
        for i, med in enumerate(medicamentos, 1):
            print(f"  {i}. Consecutivo: {med.consecutivo}, Valor: ${med.vr_servicio:,.2f}, Código: {med.cod_tecnologia_salud}")
        
        # Procedimientos
        procedimientos = RipsProcedimiento.objects.filter(factura=ultima_factura)
        print(f"\nProcedimientos: {procedimientos.count()}")
        for i, proc in enumerate(procedimientos, 1):
            print(f"  {i}. Consecutivo: {proc.consecutivo}, Valor: ${proc.vr_servicio:,.2f}, Código: {proc.cod_procedimiento}")
        
        # Hospitalización
        hospitalizaciones = RipsHospitalizacion.objects.filter(factura=ultima_factura)
        print(f"\nHospitalizaciones: {hospitalizaciones.count()}")
        for i, hosp in enumerate(hospitalizaciones, 1):
            print(f"  {i}. Consecutivo: {hosp.consecutivo}, Valor: ${hosp.vr_servicio:,.2f}, Vía ingreso: {hosp.via_ingreso_servicio}")
        
        # Otros servicios
        otros = RipsOtroServicio.objects.filter(factura=ultima_factura)
        print(f"\nOtros servicios: {otros.count()}")
        for i, otro in enumerate(otros, 1):
            print(f"  {i}. Consecutivo: {otro.consecutivo}, Valor: ${otro.vr_servicio:,.2f}, Tipo: {otro.tipo_os}")
        
        # Calcular total
        total_consultas = sum(c.vr_servicio for c in consultas)
        total_medicamentos = sum(m.vr_servicio for m in medicamentos)
        total_procedimientos = sum(p.vr_servicio for p in procedimientos)
        total_hospitalizaciones = sum(h.vr_servicio for h in hospitalizaciones)
        total_otros = sum(o.vr_servicio for o in otros)
        
        total_rips = total_consultas + total_medicamentos + total_procedimientos + total_hospitalizaciones + total_otros
        
        print(f"\n=== RESUMEN FINANCIERO ===")
        print(f"Total Consultas: ${total_consultas:,.2f}")
        print(f"Total Medicamentos: ${total_medicamentos:,.2f}")
        print(f"Total Procedimientos: ${total_procedimientos:,.2f}")
        print(f"Total Hospitalizaciones: ${total_hospitalizaciones:,.2f}")
        print(f"Total Otros servicios: ${total_otros:,.2f}")
        print(f"TOTAL RIPS: ${total_rips:,.2f}")
        print(f"Valor bruto factura: ${ultima_factura.valor_bruto:,.2f}")
        
        if abs(total_rips - ultima_factura.valor_bruto) < 0.01:
            print("✓ Los valores coinciden perfectamente")
        else:
            print(f"⚠️  Diferencia: ${abs(total_rips - ultima_factura.valor_bruto):,.2f}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_ultima_factura() 