from .models import Factura, Paciente, Contrato, RipsConsulta, RipsMedicamento, RipsProcedimiento, RipsHospitalizacion, RipsOtroServicio
from accounts.models import CatalogoCUPS, CatalogoCIE10, CatalogoCUMS, CatalogoMunicipio, CatalogoPais
from datetime import datetime, date

def validate_rips_item(item_data, item_type):
    errors = []

    # Validaciones comunes para todos los tipos de RIPS
    if not item_data.get("codPrestador"):
        errors.append("Código de Prestador es obligatorio.")
    if item_data.get("vrServicio") is None:
        errors.append("Valor del Servicio es obligatorio.")

    # Validaciones específicas por tipo de RIPS
    if item_type == "consultas":
        if not item_data.get("codConsulta"):
            errors.append("Código de Consulta (CUPS) es obligatorio.")
        # Ejemplo de validación contra catálogo (asumiendo que están poblados)
        if item_data.get("codConsulta") and not CatalogoCUPS.objects.filter(codigo=item_data["codConsulta"]).exists():
            errors.append(f"Código CUPS de Consulta '{item_data['codConsulta']}' no encontrado en el catálogo.")
        if item_data.get("codDiagnosticoPrincipal") and not CatalogoCIE10.objects.filter(codigo=item_data["codDiagnosticoPrincipal"]).exists():
            errors.append(f"Código CIE10 de Diagnóstico Principal '{item_data['codDiagnosticoPrincipal']}' no encontrado en el catálogo.")

    elif item_type == "medicamentos":
        if not item_data.get("codTecnologiaSalud"):
            errors.append("Código de Tecnología en Salud (CUMS) es obligatorio para Medicamentos.")
        if item_data.get("codTecnologiaSalud") and not CatalogoCUMS.objects.filter(codigo=item_data["codTecnologiaSalud"]).exists():
            errors.append(f"Código CUMS '{item_data['codTecnologiaSalud']}' no encontrado en el catálogo de medicamentos.")
        if item_data.get("idMIPRES") and not item_data.get("numAutorizacion"):
            errors.append("Si ID MIPRES está presente, Número de Autorización es obligatorio.")
        if item_data.get("vrUnitMedicamento") is None or item_data.get("cantidadMedicamento") is None:
             errors.append("Valor Unitario y Cantidad de Medicamento son obligatorios.")
        elif (item_data.get("vrUnitMedicamento") * item_data.get("cantidadMedicamento")) != item_data.get("vrServicio"):
             errors.append("Valor del servicio no coincide con (valor unitario * cantidad) para medicamento.")

    elif item_type == "procedimientos":
        if not item_data.get("codProcedimiento"):
            errors.append("Código de Procedimiento (CUPS) es obligatorio.")
        if item_data.get("codProcedimiento") and not CatalogoCUPS.objects.filter(codigo=item_data["codProcedimiento"]).exists():
            errors.append(f"Código CUPS de Procedimiento '{item_data['codProcedimiento']}' no encontrado en el catálogo.")

    elif item_type == "hospitalizacion":
        fecha_inicio_atencion_str = item_data.get("fechaInicioAtencion")
        fecha_egreso_str = item_data.get("fechaEgreso")
        
        if fecha_inicio_atencion_str and fecha_egreso_str:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio_atencion_str, '%Y-%m-%d %H:%M')
                fecha_egreso = datetime.strptime(fecha_egreso_str, '%Y-%m-%d %H:%M')
                if fecha_egreso < fecha_inicio:
                    errors.append("Fecha de Egreso no puede ser anterior a la Fecha de Ingreso en hospitalización.")
            except ValueError:
                errors.append("Formato de fecha/hora inválido en hospitalización.")

    elif item_type == "otrosServicios":
        if item_data.get("vrUnitOS") is None or item_data.get("cantidadOS") is None:
             errors.append("Valor Unitario y Cantidad de Otros Servicios son obligatorios.")
        elif (item_data.get("vrUnitOS") * item_data.get("cantidadOS")) != item_data.get("vrServicio"):
             errors.append("Valor del servicio no coincide con (valor unitario * cantidad) para otros servicios.")

    return errors

def validate_rips_user(user_data):
    errors = []

    if not user_data.get("tipoDocumentoIdentificacion"):
        errors.append("Tipo de Documento de Identificación es obligatorio para el usuario.")
    if not user_data.get("numDocumentoIdentificacion"):
        errors.append("Número de Documento de Identificación es obligatorio para el usuario.")
    if not user_data.get("tipoUsuario"):
        errors.append("Tipo de Usuario (Régimen) es obligatorio.")

    # Validar códigos de país y municipio (asumiendo que los catálogos están poblados)
    if user_data.get("codPaisResidencia") and not CatalogoPais.objects.filter(codigo=user_data["codPaisResidencia"]).exists():
        errors.append(f"Código de País de Residencia '{user_data['codPaisResidencia']}' no encontrado en el catálogo.")
    if user_data.get("codMunicipioResidencia") and not CatalogoMunicipio.objects.filter(codigo=user_data["codMunicipioResidencia"]).exists():
        errors.append(f"Código de Municipio de Residencia '{user_data['codMunicipioResidencia']}' no encontrado en el catálogo.")

    return errors 