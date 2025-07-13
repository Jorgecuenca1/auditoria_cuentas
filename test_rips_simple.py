#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auditoria_cuentas.settings')
django.setup()

from facturacion.models import *
from auditoria.models import *
import json

# Datos RIPS del usuario
rips_data = {
    "numDocumentoIdObligado": "892000501",
    "numFactura": "HDVE1158071",
    "tipoNota": None,
    "numNota": None,
    "usuarios": [{
        "tipoDocumentoIdentificacion": "CC",
        "numDocumentoIdentificacion": "86011109",
        "tipoUsuario": "11",
        "fechaNacimiento": "1979-07-23",
        "codSexo": "M",
        "codPaisResidencia": "170",
        "codMunicipioResidencia": "50001",
        "codZonaTerritorialResidencia": "02",
        "incapacidad": "SI",
        "consecutivo": 1,
        "codPaisOrigen": "170",
        "servicios": {
            "consultas": [{
                "codPrestador": "500010052901",
                "fechaInicioAtencion": "2025-04-06 12:13",
                "numAutorizacion": "9682493",
                "codConsulta": "890701",
                "modalidadGrupoServicioTecSal": "01",
                "grupoServicios": "05",
                "codServicio": 1102,
                "finalidadTecnologiaSalud": "15",
                "causaMotivoAtencion": "38",
                "codDiagnosticoPrincipal": "R103",
                "codDiagnosticoRelacionado1": None,
                "codDiagnosticoRelacionado2": None,
                "codDiagnosticoRelacionado3": None,
                "tipoDiagnosticoPrincipal": "01",
                "tipoDocumentoIdentificacion": "CC",
                "numDocumentoIdentificacion": "1121917926",
                "vrServicio": 84152,
                "conceptoRecaudo": "05",
                "valorPagoModerador": 0,
                "numFEVPagoModerador": None,
                "consecutivo": 1
            }],
            "medicamentos": [{
                "codPrestador": "500010052901",
                "numAutorizacion": "9682493",
                "idMIPRES": None,
                "fechaDispensAdmon": "2025-04-06 09:08",
                "codDiagnosticoPrincipal": "R103",
                "codDiagnosticoRelacionado": None,
                "tipoMedicamento": "01",
                "codTecnologiaSalud": "000",
                "nomTecnologiaSalud": None,
                "concentracionMedicamento": 0,
                "unidadMedida": 0,
                "formaFarmaceutica": None,
                "unidadMinDispensa": 74,
                "cantidadMedicamento": 1,
                "diasTratamiento": 1,
                "tipoDocumentoIdentificacion": "CC",
                "numDocumentoIdentificacion": "1121917926",
                "vrUnitMedicamento": 8867,
                "vrServicio": 8867,
                "conceptoRecaudo": "05",
                "valorPagoModerador": 0,
                "numFEVPagoModerador": None,
                "consecutivo": 1
            }],
            "procedimientos": [{
                "codPrestador": "500010052901",
                "fechaInicioAtencion": "2025-04-06 08:10",
                "idMIPRES": None,
                "numAutorizacion": "9682493",
                "codProcedimiento": "902210",
                "viaIngresoServicioSalud": "03",
                "modalidadGrupoServicioTecSal": "01",
                "grupoServicios": "02",
                "codServicio": 706,
                "finalidadTecnologiaSalud": "15",
                "tipoDocumentoIdentificacion": "CC",
                "numDocumentoIdentificacion": "1121917926",
                "codDiagnosticoPrincipal": "R103",
                "codDiagnosticoRelacionado": None,
                "codComplicacion": None,
                "vrServicio": 32303,
                "conceptoRecaudo": "05",
                "valorPagoModerador": 0,
                "numFEVPagoModerador": None,
                "consecutivo": 1
            }],
            "hospitalizacion": [{
                "codPrestador": "500010052901",
                "viaIngresoServicioSalud": "03",
                "fechaInicioAtencion": "2025-04-06 07:36",
                "numAutorizacion": "9682493",
                "causaMotivoAtencion": "38",
                "codDiagnosticoPrincipal": "R103",
                "codDiagnosticoPrincipalE": "R103",
                "codDiagnosticoRelacionadoE1": None,
                "codDiagnosticoRelacionadoE2": None,
                "codDiagnosticoRelacionadoE3": None,
                "codComplicacion": None,
                "condicionDestinoUsuarioEgreso": "01",
                "codDiagnosticoCausaMuerte": None,
                "fechaEgreso": "2025-04-08 13:51",
                "consecutivo": 1
            }],
            "otrosServicios": [{
                "codPrestador": "500010052901",
                "numAutorizacion": "9682493",
                "idMIPRES": None,
                "fechaSuministroTecnologia": "2025-04-06 09:08",
                "tipoOS": "01",
                "codTecnologiaSalud": "UT1518020010972",
                "nomTecnologiaSalud": "EQUIPO DE EXTENSION DE ANESTESIA REF ARCO473MP",
                "cantidadOS": 1,
                "tipoDocumentoIdentificacion": "CC",
                "numDocumentoIdentificacion": "1121917926",
                "vrUnitOS": 9590,
                "vrServicio": 9590,
                "conceptoRecaudo": "05",
                "valorPagoModerador": 0,
                "numFEVPagoModerador": None,
                "consecutivo": 1
            }]
        }
    }]
}

print("=== ANÁLISIS DE RIPS ===")
print(f"Número de factura: {rips_data['numFactura']}")
print(f"Número de usuarios: {len(rips_data.get('usuarios', []))}")

for user in rips_data.get('usuarios', []):
    servicios = user.get('servicios', {})
    print(f"\nServicios disponibles: {list(servicios.keys())}")
    for service_type, items in servicios.items():
        print(f"  {service_type}: {len(items)} items")

# Verificar si ya existe factura
try:
    factura_existente = Factura.objects.get(numero=rips_data['numFactura'])
    print(f"\n⚠️  FACTURA YA EXISTE: {factura_existente.numero}")
    print(f"   Estado: {factura_existente.estado}")
    print(f"   Fecha radicación: {factura_existente.fecha_radicacion}")
    
    # Verificar RIPS existentes
    consultas = RipsConsulta.objects.filter(factura=factura_existente).count()
    medicamentos = RipsMedicamento.objects.filter(factura=factura_existente).count()
    procedimientos = RipsProcedimiento.objects.filter(factura=factura_existente).count()
    hospitalizacion = RipsHospitalizacion.objects.filter(factura=factura_existente).count()
    otros_servicios = RipsOtroServicio.objects.filter(factura=factura_existente).count()
    
    print(f"\n📊 RIPS EXISTENTES EN BD:")
    print(f"   Consultas: {consultas}")
    print(f"   Medicamentos: {medicamentos}")
    print(f"   Procedimientos: {procedimientos}")
    print(f"   Hospitalización: {hospitalizacion}")
    print(f"   Otros servicios: {otros_servicios}")
    
except Factura.DoesNotExist:
    print(f"\n✅ FACTURA NO EXISTE: {rips_data['numFactura']}")
    print("   Se puede procesar normalmente") 