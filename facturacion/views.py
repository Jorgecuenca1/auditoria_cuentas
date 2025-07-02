from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Factura, Paciente, Contrato, RipsConsulta, RipsMedicamento, RipsProcedimiento, RipsHospitalizacion, RipsOtroServicio, TarifaContrato
from .forms import FacturaForm, RipsUploadForm, ContratoForm, TarifaContratoForm
from accounts.models import Profile, CatalogoCUPS, CatalogoCIE10, CatalogoCUMS, CatalogoMunicipio, CatalogoPais
from .validators import validate_rips_item, validate_rips_user
import json
from datetime import datetime, date
from django.contrib.auth.decorators import login_required

def parse_date_time(dt_str):
    if not dt_str:
        return None
    try:
        return datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
    except ValueError:
        try:
            return datetime.strptime(dt_str, '%Y-%m-%d')
        except ValueError:
            return None

def radicar_factura(request):
    if request.method == 'POST':
        form = FacturaForm(request.POST, request.FILES)
        if form.is_valid():
            factura = form.save(commit=False)
            factura.ips = request.user.profile
            factura.estado_auditoria = "Radicada"
            factura.save() # Guardar la factura aquí para que tenga un ID

            # Procesar el archivo RIPS
            archivo = factura.archivo_rips.open()
            rips_errors = [] # Lista para acumular errores de validación del RIPS
            try:
                data = json.load(archivo)

                # Procesar sección 'usuarios' para Paciente records y validar
                # El paciente principal de la factura se asigna con el primer usuario encontrado.
                # Los pacientes de los ítems de servicio se manejarán individualmente.
                factura_main_paciente = None

                for user_data in data.get("usuarios", []):
                    user_validation_errors = validate_rips_user(user_data)
                    if user_validation_errors:
                        rips_errors.append(f"Errores en datos de usuario ({user_data.get('numDocumentoIdentificacion')}): {'; '.join(user_validation_errors)}")
                        continue # Saltar a la siguiente usuario si hay errores críticos en sus datos

                    # Crear o obtener el paciente principal de la factura si aún no está asignado
                    if not factura_main_paciente:
                        paciente_obj, created = Paciente.objects.get_or_create(
                            tipo_documento=user_data.get("tipoDocumentoIdentificacion", ""),
                            numero_documento=user_data.get("numDocumentoIdentificacion", ""),
                            defaults={
                                'tipo_usuario': user_data.get("tipoUsuario", ""),
                                'fecha_nacimiento': datetime.strptime(user_data.get("fechaNacimiento", "1900-01-01"), '%Y-%m-%d').date(),
                                'sexo': user_data.get("codSexo", ""),
                                'pais_residencia': user_data.get("codPaisResidencia", ""),
                                'municipio_residencia': user_data.get("codMunicipioResidencia", ""),
                                'zona_territorial': user_data.get("codZonaTerritorialResidencia", ""),
                                'incapacidad': user_data.get("incapacidad", ""),
                                'pais_origen': user_data.get("codPaisOrigen", ""),
                            }
                        )
                        factura_main_paciente = paciente_obj
                        if not factura.paciente:
                            factura.paciente = factura_main_paciente

                    # Procesar 'servicios' para Rips* items y validar
                    servicios = user_data.get("servicios", {})
                    for service_type, items_list in servicios.items():
                        for item_data in items_list:
                            item_validation_errors = validate_rips_item(item_data, service_type)
                            if item_validation_errors:
                                rips_errors.append(f"Errores en ítem {service_type} (consecutivo: {item_data.get('consecutivo')}, Paciente: {item_data.get('numDocumentoIdentificacion')}): {'; '.join(item_validation_errors)}")
                                # No usamos 'continue' aquí para permitir guardar el ítem para propósitos de prueba.

                            try:
                                # Obtener o crear el paciente específico para este ítem de servicio
                                item_paciente, created = Paciente.objects.get_or_create(
                                    tipo_documento=item_data.get("tipoDocumentoIdentificacion", ""),
                                    numero_documento=item_data.get("numDocumentoIdentificacion", ""),
                                    defaults={
                                        # Campos por defecto si es un paciente nuevo del ítem
                                        # Puedes rellenar estos campos con lógica adicional si tu JSON lo permite
                                        'tipo_usuario': user_data.get("tipoUsuario", ""), # Se asume el tipo de usuario del bloque principal
                                        'fecha_nacimiento': datetime.strptime(user_data.get("fechaNacimiento", "1900-01-01"), '%Y-%m-%d').date(), # Asume fecha de nacimiento del principal
                                        'sexo': user_data.get("codSexo", ""),
                                        'pais_residencia': user_data.get("codPaisResidencia", ""),
                                        'municipio_residencia': user_data.get("codMunicipioResidencia", ""),
                                        'zona_territorial': user_data.get("codZonaTerritorialResidencia", ""),
                                        'incapacidad': user_data.get("incapacidad", ""),
                                        'pais_origen': user_data.get("codPaisOrigen", ""),
                                    }
                                )

                                common_fields = {
                                    'factura': factura,
                                    'paciente': item_paciente, # Asociar al paciente específico del ítem
                                    'cod_prestador': item_data.get("codPrestador", ""),
                                    'num_autorizacion': item_data.get("numAutorizacion", ""),
                                    'vr_servicio': item_data.get("vrServicio", 0) if item_data.get("vrServicio") is not None else 0,
                                    'concepto_recaudo': item_data.get("conceptoRecaudo", ""),
                                    'valor_pago_moderador': item_data.get("valorPagoModerador", 0) if item_data.get("valorPagoModerador") is not None else 0,
                                    'consecutivo': item_data.get("consecutivo", 0) if item_data.get("consecutivo") is not None else 0,
                                }

                                if service_type == "consultas":
                                    RipsConsulta.objects.create(
                                        **common_fields,
                                        fecha_inicio_atencion=parse_date_time(item_data.get("fechaInicioAtencion")),
                                        cod_consulta=item_data.get("codConsulta", "") or "", # Asegurar string no nulo
                                        modalidad_grupo_servicio=item_data.get("modalidadGrupoServicioTecSal", "") or "",
                                        grupo_servicios=item_data.get("grupoServicios", "") or "",
                                        cod_servicio=item_data.get("codServicio", "") or "",
                                        finalidad_tecnologia=item_data.get("finalidadTecnologiaSalud", "") or "",
                                        causa_motivo_atencion=item_data.get("causaMotivoAtencion", "") or "",
                                        cod_diagnostico_principal=item_data.get("codDiagnosticoPrincipal", "") or "",
                                        tipo_diagnostico_principal=item_data.get("tipoDiagnosticoPrincipal", "") or "",
                                    )
                                elif service_type == "medicamentos":
                                    RipsMedicamento.objects.create(
                                        **common_fields,
                                        id_mipres=item_data.get("idMIPRES", "") or "", # Asegurar string no nulo
                                        fecha_dispensacion=parse_date_time(item_data.get("fechaDispensAdmon")),
                                        cod_diagnostico_principal=item_data.get("codDiagnosticoPrincipal", "") or "",
                                        tipo_medicamento=item_data.get("tipoMedicamento", "") or "",
                                        cod_tecnologia_salud=item_data.get("codTecnologiaSalud", "") or "",
                                        nom_tecnologia_salud=item_data.get("nomTecnologiaSalud", "") or "",
                                        concentracion_medicamento=item_data.get("concentracionMedicamento", "") or "",
                                        unidad_medida=item_data.get("unidadMedida", "") or "",
                                        forma_farmaceutica=item_data.get("formaFarmaceutica", "") or "",
                                        unidad_min_dispensa=item_data.get("unidadMinDispensa", 0) if item_data.get("unidadMinDispensa") is not None else 0,
                                        cantidad_medicamento=item_data.get("cantidadMedicamento", 0) if item_data.get("cantidadMedicamento") is not None else 0,
                                        dias_tratamiento=item_data.get("diasTratamiento", 0) if item_data.get("diasTratamiento") is not None else 0,
                                        vr_unit_medicamento=item_data.get("vrUnitMedicamento", 0) if item_data.get("vrUnitMedicamento") is not None else 0,
                                    )
                                elif service_type == "procedimientos":
                                    RipsProcedimiento.objects.create(
                                        **common_fields,
                                        fecha_inicio_atencion=parse_date_time(item_data.get("fechaInicioAtencion")),
                                        cod_procedimiento=item_data.get("codProcedimiento", "") or "",
                                        via_ingreso_servicio=item_data.get("viaIngresoServicioSalud", "") or "",
                                        modalidad_grupo_servicio=item_data.get("modalidadGrupoServicioTecSal", "") or "",
                                        grupo_servicios=item_data.get("grupoServicios", "") or "",
                                        cod_servicio=item_data.get("codServicio", "") or "",
                                        finalidad_tecnologia=item_data.get("finalidadTecnologiaSalud", "") or "",
                                        cod_diagnostico_principal=item_data.get("codDiagnosticoPrincipal", "") or "",
                                    )
                                elif service_type == "hospitalizacion":
                                    RipsHospitalizacion.objects.create(
                                        **common_fields,
                                        via_ingreso_servicio=item_data.get("viaIngresoServicioSalud", "") or "",
                                        fecha_inicio_atencion=parse_date_time(item_data.get("fechaInicioAtencion")) or datetime(1900, 1, 1, 0, 0),
                                        causa_motivo_atencion=item_data.get("causaMotivoAtencion", "") or "",
                                        cod_diagnostico_principal=item_data.get("codDiagnosticoPrincipal", "") or "",
                                        cod_diagnostico_principal_e=item_data.get("codDiagnosticoPrincipalE", "") or "",
                                        condicion_destino_egreso=item_data.get("condicionDestinoUsuarioEgreso", "") or "",
                                        fecha_egreso=parse_date_time(item_data.get("fechaEgreso")) or datetime(1900, 1, 1, 0, 0),
                                    )
                                elif service_type == "otrosServicios":
                                    RipsOtroServicio.objects.create(
                                        **common_fields,
                                        id_mipres=item_data.get("idMIPRES", "") or "",
                                        fecha_suministro=parse_date_time(item_data.get("fechaSuministroTecnologia")),
                                        tipo_os=item_data.get("tipoOS", "") or "",
                                        cod_tecnologia_salud=item_data.get("codTecnologiaSalud", "") or "",
                                        nom_tecnologia_salud=item_data.get("nomTecnologiaSalud", "") or "",
                                        cantidad_os=item_data.get("cantidadOS", 0) if item_data.get("cantidadOS") is not None else 0,
                                        vr_unit_os=item_data.get("vrUnitOS", 0) if item_data.get("vrUnitOS") is not None else 0,
                                    )
                                # Aquí se podrían añadir más tipos de RIPS (urgencias, recién nacidos, etc.)

                            except Exception as e:
                                rips_errors.append(f"Error interno al guardar ítem de RIPS (tipo: {service_type}, consecutivo: {item_data.get('consecutivo')}, Paciente: {item_data.get('numDocumentoIdentificacion')}): {e}")
                                # Considerar registrar el error en un log para depuración
                                # No usamos 'continue' aquí para permitir guardar el ítem para propósitos de prueba.

                if rips_errors: # Si hay errores de validación, mostrar advertencias pero permitir guardar
                    for error_msg in rips_errors:
                        messages.warning(request, error_msg) # Cambiado a warning
                    messages.success(request, "Factura radicada con advertencias en el archivo RIPS.") # Mensaje de éxito/advertencia
                    return redirect('facturacion:radicar_factura') # O a una página de éxito
                else:
                    messages.success(request, "Factura y RIPS cargados exitosamente.")
                    return redirect('facturacion:radicar_factura') # O a una página de éxito

            except json.JSONDecodeError:
                messages.error(request, "El archivo RIPS no es un JSON válido.")
            except Exception as e:
                messages.error(request, f"Ocurrió un error inesperado al procesar el archivo RIPS: {e}")
        else:
            messages.error(request, "Error en el formulario de la factura. Por favor, revisa los datos.")
    else:
        form = FacturaForm()

    return render(request, 'facturacion/radicar_factura.html', {'form': form})

@login_required
def contrato_list(request):
    contratos = Contrato.objects.all().order_by('-fecha_inicio')
    return render(request, 'facturacion/contrato_list.html', {'contratos': contratos})

@login_required
def contrato_create(request):
    if request.method == 'POST':
        form = ContratoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Contrato creado exitosamente.")
            return redirect('facturacion:contrato_list')
    else:
        form = ContratoForm()
    return render(request, 'facturacion/contrato_form.html', {'form': form, 'title': 'Crear Contrato'})

@login_required
def contrato_update(request, pk):
    contrato = get_object_or_404(Contrato, pk=pk)
    if request.method == 'POST':
        form = ContratoForm(request.POST, request.FILES, instance=contrato)
        if form.is_valid():
            form.save()
            messages.success(request, "Contrato actualizado exitosamente.")
            return redirect('facturacion:contrato_list')
    else:
        form = ContratoForm(instance=contrato)
    tarifas = TarifaContrato.objects.filter(contrato=contrato)
    return render(request, 'facturacion/contrato_form.html', {'form': form, 'title': 'Editar Contrato', 'contrato': contrato, 'tarifas': tarifas})

@login_required
def tarifa_contrato_list(request, contrato_pk):
    contrato = get_object_or_404(Contrato, pk=contrato_pk)
    tarifas = TarifaContrato.objects.filter(contrato=contrato)
    return render(request, 'facturacion/tarifa_contrato_list.html', {'contrato': contrato, 'tarifas': tarifas})

@login_required
def tarifa_contrato_create(request, contrato_pk):
    contrato = get_object_or_404(Contrato, pk=contrato_pk)
    if request.method == 'POST':
        form = TarifaContratoForm(request.POST)
        if form.is_valid():
            tarifa = form.save(commit=False)
            tarifa.contrato = contrato
            tarifa.save()
            messages.success(request, "Tarifa creada exitosamente.")
            return redirect('facturacion:contrato_update', pk=contrato.pk) # Redirigir de vuelta al contrato
    else:
        form = TarifaContratoForm()
    return render(request, 'facturacion/tarifa_contrato_form.html', {'form': form, 'title': 'Crear Tarifa', 'contrato': contrato})

@login_required
def tarifa_contrato_update(request, pk):
    tarifa = get_object_or_404(TarifaContrato, pk=pk)
    contrato = tarifa.contrato
    if request.method == 'POST':
        form = TarifaContratoForm(request.POST, instance=tarifa)
        if form.is_valid():
            form.save()
            messages.success(request, "Tarifa actualizada exitosamente.")
            return redirect('facturacion:contrato_update', pk=contrato.pk)
    else:
        form = TarifaContratoForm(instance=tarifa)
    return render(request, 'facturacion/tarifa_contrato_form.html', {'form': form, 'title': 'Editar Tarifa', 'contrato': contrato})

@login_required
def tarifa_contrato_delete(request, pk):
    tarifa = get_object_or_404(TarifaContrato, pk=pk)
    contrato_pk = tarifa.contrato.pk
    if request.method == 'POST':
        tarifa.delete()
        messages.success(request, "Tarifa eliminada exitosamente.")
        return redirect('facturacion:contrato_update', pk=contrato_pk)
    return render(request, 'facturacion/confirm_delete.html', {'object': tarifa, 'contrato_pk': contrato_pk})
