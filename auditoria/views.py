from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from facturacion.models import Factura, Paciente, RipsConsulta, RipsMedicamento, RipsProcedimiento, RipsHospitalizacion, RipsOtroServicio, Devolucion, CodigoDevolucion, SubcodigoDevolucion, Lote
from .models import Glosa, TipoGlosa, SubtipoGlosa, SubCodigoGlosa, TipoGlosaRespuestaIPS, SubtipoGlosaRespuestaIPS, HistorialGlosa
from .forms import TipoAuditoriaForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum, Count, F, Case, When, Value, CharField
from accounts.decorators import role_required
from decimal import Decimal # Importar Decimal


@login_required
@role_required('ET')
def reporte_glosas(request):
    # Estadísticas generales de glosas
    total_glosas = Glosa.objects.count()
    glosas_pendientes = Glosa.objects.filter(estado="Pendiente").count()
    glosas_respondidas = Glosa.objects.filter(estado="Respondida").count() # Esto necesitará ajustarse a los nuevos estados
    valor_total_glosado = Glosa.objects.aggregate(total=Sum('valor_glosado'))['total'] or 0

    # Glosas por IPS (factura__ips se refiere al Profile)
    glosas_por_ips = Glosa.objects.values(
        'factura__ips__entidad_nombre'
    ).annotate(
        total_glosas=Count('id'),
        valor_total=Sum('valor_glosado')
    ).order_by('-valor_total')

    return render(request, 'auditoria/reportes/reporte_glosas.html', {
        'total_glosas': total_glosas,
        'glosas_pendientes': glosas_pendientes,
        'glosas_respondidas': glosas_respondidas,
        'valor_total_glosado': valor_total_glosado,
        'glosas_por_ips': glosas_por_ips,
    })

@login_required
@role_required('ET')
def reporte_cartera(request):
    # Estadísticas de cartera
    facturas = Factura.objects.all()
    total_facturas = facturas.count()
    valor_total = facturas.aggregate(total=Sum('valor_bruto'))['total'] or 0
    
    # Cartera por IPS
    cartera_por_ips = facturas.values(
        'ips__entidad_nombre'
    ).annotate(
        total_facturas=Count('id'),
        valor_total=Sum('valor_bruto')
    ).order_by('-valor_total')

    # Cartera por estado de auditoría
    cartera_por_estado = facturas.values(
        'estado'
    ).annotate(
        total_facturas=Count('id'),
        valor_total=Sum('valor_bruto')
    ).order_by('estado')

    return render(request, 'auditoria/reportes/reporte_cartera.html', {
        'total_facturas': total_facturas,
        'valor_total': valor_total,
        'cartera_por_ips': cartera_por_ips,
        'cartera_por_estado': cartera_por_estado,
    })

@login_required
@role_required('ET')
def reporte_auditorias(request):
    # Estadísticas de auditorías
    facturas = Factura.objects.all()
    total_auditadas = facturas.filter(estado='Auditada').count()
    total_pendientes = facturas.exclude(estado='Auditada').count()
    
    # Auditorías por IPS
    auditorias_por_ips = facturas.values(
        'ips__entidad_nombre',
        'estado'
    ).annotate(
        total=Count('id'),
        valor_total=Sum('valor_bruto')
    ).order_by('ips__entidad_nombre', 'estado')

    return render(request, 'auditoria/reportes/reporte_auditorias.html', {
        'total_auditadas': total_auditadas,
        'total_pendientes': total_pendientes,
        'auditorias_por_ips': auditorias_por_ips,
    })

# NUEVO: Reporte de Glosas por Paciente
@login_required
@role_required('ET')
def reporte_glosas_por_paciente(request):
    glosas_por_paciente = Glosa.objects.values(
        'paciente__numero_documento',
        'paciente__tipo_usuario' # Para diferenciar régimen
    ).annotate(
        total_glosas=Count('id'),
        valor_total_glosado=Sum('valor_glosado')
    ).order_by('-valor_total_glosado')

    return render(request, 'auditoria/reportes/reporte_glosas_por_paciente.html', {
        'glosas_por_paciente': glosas_por_paciente
    })

# NUEVO: Reporte de Glosas por Tipo de Ítem RIPS
@login_required
@role_required('ET')
def reporte_glosas_por_tipo_item(request):
    glosas_por_tipo = Glosa.objects.annotate(
        item_type=Case(
            When(consulta__isnull=False, then=Value('Consulta')),
            When(medicamento__isnull=False, then=Value('Medicamento')),
            When(procedimiento__isnull=False, then=Value('Procedimiento')),
            When(hospitalizacion__isnull=False, then=Value('Hospitalización')),
            When(otro_servicio__isnull=False, then=Value('Otros Servicios')),
            default=Value('General'),
            output_field=CharField(),
        )
    ).values('item_type').annotate(
        total_glosas=Count('id'),
        valor_total_glosado=Sum('valor_glosado')
    ).order_by('-total_glosas')

    return render(request, 'auditoria/reportes/reporte_glosas_por_tipo_item.html', {
        'glosas_por_tipo': glosas_por_tipo
    })

@login_required
@role_required(['ET', 'AUDITOR'])
def lista_radicados(request):
    sort_by = request.GET.get('sort', 'fecha_radicacion')
    order = request.GET.get('order', 'desc')
    order_by_string = f"{'-' if order == 'desc' else ''}{sort_by}"

    facturas_base_query = Factura.objects.select_related('ips', 'lote', 'auditor', 'paciente')
    
    if request.user.profile.role == 'AUDITOR':
        facturas_list = facturas_base_query.filter(auditor=request.user).order_by(order_by_string)
    else:
        facturas_list = facturas_base_query.all().order_by(order_by_string)

    if request.method == 'POST':
        factura_id = request.POST.get('factura_id')
        factura = get_object_or_404(Factura, pk=factura_id)

        # Manejar asignación de auditor
        if 'asignar_auditor' in request.POST:
            auditor_id = request.POST.get('auditor_id')
            if auditor_id:
                auditor = get_object_or_404(User, pk=auditor_id, profile__role='AUDITOR')
                factura.auditor = auditor
                factura.save()
                messages.success(request, f'Auditor "{auditor.get_full_name() or auditor.username}" asignado a la factura {factura.numero}.')
            else: # Des-asignar
                factura.auditor = None
                factura.save()
                messages.info(request, f'Se ha quitado el auditor de la factura {factura.numero}.')
            return redirect(request.META.get('HTTP_REFERER', 'auditoria:lista_radicados'))

        # Manejar actualización de tipo de auditoría
        if 'guardar_tipo_auditoria' in request.POST:
            form = TipoAuditoriaForm(request.POST, instance=factura, prefix=f'tipo_auditoria_{factura_id}')
            if form.is_valid():
                form.save()
                messages.success(request, f"Se actualizó el tipo de auditoría para la factura {factura.numero}.")
            else:
                messages.error(request, f"Hubo un error al actualizar el tipo de auditoría: {form.errors.as_text()}")
            return redirect(request.META.get('HTTP_REFERER', 'auditoria:lista_radicados'))


    # Preparar datos combinados para la plantilla
    facturas_con_forms = []
    for factura in facturas_list:
        facturas_con_forms.append({
            'factura': factura,
            'tipo_auditoria_form': TipoAuditoriaForm(instance=factura, prefix=f'tipo_auditoria_{factura.id}'),
        })

    # Contadores para la UI
    total_facturas = facturas_list.count()
    total_auditadas = facturas_list.filter(estado='Auditada').count()
    total_pendientes = facturas_list.exclude(estado='Auditada').count()

    auditores = User.objects.filter(profile__role='AUDITOR')
    codigos_devolucion = CodigoDevolucion.objects.prefetch_related('subcodigos').all()

    context = {
        'facturas_con_forms': facturas_con_forms,
        'auditores': auditores,
        'codigos_devolucion': codigos_devolucion,
        'total_facturas': total_facturas,
        'total_auditadas': total_auditadas,
        'total_pendientes': total_pendientes,
        'current_sort': sort_by,
        'current_order': order,
    }
    return render(request, 'auditoria/lista_radicados.html', context)


@login_required
@role_required(['ET','AUDITOR'])
def auditar_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    tipos_glosa = TipoGlosa.objects.all()
    consultas = RipsConsulta.objects.filter(factura=factura)
    medicamentos = RipsMedicamento.objects.filter(factura=factura)
    procedimientos = RipsProcedimiento.objects.filter(factura=factura)
    hospitalizaciones = RipsHospitalizacion.objects.filter(factura=factura)
    otros_servicios = RipsOtroServicio.objects.filter(factura=factura)
    all_rips_items = list(consultas) + list(medicamentos) + list(procedimientos) + list(hospitalizaciones) + list(otros_servicios)
    identificaciones = sorted(set(item.paciente.numero_documento for item in all_rips_items if item.paciente))
    
    if request.method == 'POST':
        if 'finalizar_auditoria' in request.POST:
            # Remove the check for pending glosas as per the revised workflow
            # glosas_pendientes = Glosa.objects.filter(factura=factura, estado="Pendiente").exists()
            # if glosas_pendientes:
            #     messages.error(request, "No se puede finalizar la auditoría mientras haya glosas pendientes por responder.")
            # else:
            factura.estado = 'Auditada'
            factura.save()
            messages.success(request, "Auditoría finalizada exitosamente.")
            return redirect('auditoria:lista_radicados')
        elif factura.estado != 'Auditada': # Solo permitir crear glosas si la auditoría no está finalizada
            item_type = request.POST.get('item_type')
            item_pk = request.POST.get('item_pk')
            descripcion = request.POST.get('descripcion')
            valor_glosado = request.POST.get('valor_glosado')
            tipo_glosa_id = request.POST.get('tipo_glosa')
            subtipo_glosa_id = request.POST.get('subtipo_glosa')
            subcodigo_glosa_id = request.POST.get('subcodigo_glosa')
            glosa_kwargs = {
                'factura': factura,
                'descripcion': descripcion,
                'valor_glosado': valor_glosado,
                'tipo_glosa_id': tipo_glosa_id,
                'subtipo_glosa_id': subtipo_glosa_id,
                'subcodigo_glosa_id': subcodigo_glosa_id,
            }
            related_item = None
            
            # Manejar glosas generales (sin item_type o item_type == 'general')
            if not item_type or item_type == 'general':
                # Glosa general de la factura - no se asocia a ningún ítem RIPS específico
                glosa_kwargs['paciente'] = factura.paciente  # Usar paciente de la factura si existe
                messages.info(request, "Glosa general creada para toda la factura.")
            elif item_type == 'consulta' and item_pk:
                related_item = get_object_or_404(RipsConsulta, pk=item_pk)
                glosa_kwargs['consulta'] = related_item
            elif item_type == 'medicamento' and item_pk:
                related_item = get_object_or_404(RipsMedicamento, pk=item_pk)
                glosa_kwargs['medicamento'] = related_item
            elif item_type == 'procedimiento' and item_pk:
                related_item = get_object_or_404(RipsProcedimiento, pk=item_pk)
                glosa_kwargs['procedimiento'] = related_item
            elif item_type == 'hospitalizacion' and item_pk:
                related_item = get_object_or_404(RipsHospitalizacion, pk=item_pk)
                glosa_kwargs['hospitalizacion'] = related_item
            elif item_type == 'otro_servicio' and item_pk:
                related_item = get_object_or_404(RipsOtroServicio, pk=item_pk)
                glosa_kwargs['otro_servicio'] = related_item
            
            # Para glosas específicas de ítems RIPS, asociar el paciente del ítem
            if related_item and hasattr(related_item, 'paciente'):
                glosa_kwargs['paciente'] = related_item.paciente
            
            # Asignar la IPS de la factura a la glosa
            glosa_kwargs['ips'] = factura.ips
            glosa = Glosa.objects.create(**glosa_kwargs)
            
            # Registrar en el historial
            HistorialGlosa.registrar_cambio(
                glosa=glosa,
                accion='creada',
                usuario=request.user,
                descripcion_cambio=f"Glosa creada por {request.user.get_full_name() or request.user.username}",
                request=request
            )
            
            messages.success(request, "Glosa creada exitosamente.")
            return redirect('auditoria:auditar_factura', factura_id=factura.id)
        else:
            messages.error(request, "No se pueden crear nuevas glosas porque la auditoría ya fue finalizada.")
    
    glosas = Glosa.objects.filter(factura=factura).select_related('tipo_glosa', 'subtipo_glosa', 'subcodigo_glosa', 'tipo_glosa_respuesta', 'subtipo_glosa_respuesta')
    return render(request, 'auditoria/auditar_factura.html', {
        'factura': factura,
        'consultas': consultas,
        'medicamentos': medicamentos,
        'procedimientos': procedimientos,
        'hospitalizaciones': hospitalizaciones,
        'otros_servicios': otros_servicios,
        'glosas': glosas,
        'identificaciones': identificaciones,
        'tipos_glosa': tipos_glosa,
    })

@login_required
@role_required(['ET', 'AUDITOR'])
def reporte_auditoria_detalle(request, factura_id):
    factura = get_object_or_404(
        Factura.objects.select_related(
            'paciente', 'ips', 'eps', 'auditor__profile', 'devolucion__subcodigo__codigo_padre'
        ), 
        id=factura_id
    )
    glosas = Glosa.objects.filter(factura=factura).select_related(
        'tipo_glosa', 'subtipo_glosa', 'subcodigo_glosa',
        'tipo_glosa_respuesta', 'subtipo_glosa_respuesta'
    ).prefetch_related(
        'historial', 'historial__usuario'
    ).order_by('fecha_glosa')

    # Calcular estadísticas por estado considerando el flujo real de la glosa
    glosas_pendientes = glosas.filter(fecha_respuesta__isnull=True).count()
    # Una glosa está "Respondida por IPS" si tiene fecha_respuesta, independientemente del estado final
    glosas_respondidas_ips = glosas.filter(fecha_respuesta__isnull=False).count()
    # Mapear estados legacy: "Aceptada" es equivalente a "Aceptada ET"
    glosas_aceptadas_et = glosas.filter(estado__in=['Aceptada', 'Aceptada ET']).count()
    glosas_rechazadas_et = glosas.filter(estado='Rechazada ET').count()
    glosas_devueltas_ips = glosas.filter(estado='Devuelta a IPS').count()
    glosas_indefinidas = glosas.filter(estado='Indefinida').count()

    # Calcular valor total glosado original (suma de todos los valores glosados)
    valor_total_glosado_original = sum(glosa.valor_glosado for glosa in glosas)

    valor_total_glosado_definitivo = Decimal('0.00')
    for glosa in glosas:
        if glosa.estado == 'Rechazada ET':
            # Si la ET rechaza la respuesta de la IPS, el valor glosado original es definitivo
            valor_total_glosado_definitivo += glosa.valor_glosado
        elif glosa.estado in ['Aceptada', 'Aceptada ET'] and glosa.valor_aceptado_et is not None:
            # Si la ET acepta parcialmente, se usa el valor_aceptado_et (que representa lo que AUN se glosa, si la IPS no lo levantó todo)
            # Si glosa.valor_aceptado_et es 0, significa que la glosa fue completamente levantada.
            valor_total_glosado_definitivo += glosa.valor_aceptado_et
        # Glosas en 'Pendiente', 'Respondida'/'Respondida IPS', 'Devuelta a IPS', 'Indefinida' no afectan el valor definitivo de la cartera hasta que la ET decida.
        # Asumo que valor_aceptado_et en el modelo glosa representa lo que queda glosado, si es 0, la glosa se levanta.

    # Calcular el valor neto a pagar
    valor_neto_a_pagar = factura.valor_bruto - valor_total_glosado_definitivo
    if valor_neto_a_pagar < 0:
        valor_neto_a_pagar = Decimal('0.00') # Asegurar que no sea negativo

    # Calcular estadísticas del historial
    total_historial = sum(glosa.historial.count() for glosa in glosas)
    glosas_con_historial = sum(1 for glosa in glosas if glosa.historial.count() > 0)
    
    # Obtener la fecha de la última actividad
    ultima_actividad = None
    for glosa in glosas:
        for registro in glosa.historial.all():
            if ultima_actividad is None or registro.fecha_cambio > ultima_actividad:
                ultima_actividad = registro.fecha_cambio

    rips_consultas = RipsConsulta.objects.filter(factura=factura)
    rips_medicamentos = RipsMedicamento.objects.filter(factura=factura)
    rips_procedimientos = RipsProcedimiento.objects.filter(factura=factura)
    rips_hospitalizaciones = RipsHospitalizacion.objects.filter(factura=factura)
    rips_otros_servicios = RipsOtroServicio.objects.filter(factura=factura)

    context = {
        'factura': factura,
        'paciente': factura.paciente,
        'glosas': glosas,
        'glosas_pendientes': glosas_pendientes,
        'glosas_respondidas_ips': glosas_respondidas_ips,
        'glosas_aceptadas_et': glosas_aceptadas_et,
        'glosas_rechazadas_et': glosas_rechazadas_et,
        'glosas_devueltas_ips': glosas_devueltas_ips,
        'glosas_indefinidas': glosas_indefinidas,
        'valor_total_glosado_original': valor_total_glosado_original,
        'rips_consultas': rips_consultas,
        'rips_medicamentos': rips_medicamentos,
        'rips_procedimientos': rips_procedimientos,
        'rips_hospitalizaciones': rips_hospitalizaciones,
        'rips_otros_servicios': rips_otros_servicios,
        'valor_total_glosado_definitivo': valor_total_glosado_definitivo,
        'valor_neto_a_pagar': valor_neto_a_pagar,
        'total_historial': total_historial,
        'glosas_con_historial': glosas_con_historial,
        'ultima_actividad': ultima_actividad,
    }

    return render(request, 'auditoria/reportes/reporte_auditoria_detalle.html', context)

@login_required
@role_required('ET')
def reporte_auditoria_lote(request):
    # from facturacion.models import Lote # Ya importado al inicio
    lotes = Lote.objects.all().order_by('nombre')
    facturas_en_lotes = []
    selected_lotes_ids = []

    if request.method == 'POST':
        lote_ids = request.POST.getlist('lotes')
        if lote_ids:
            # Convertir IDs a enteros para la consulta
            selected_lotes_ids = [int(id) for id in lote_ids]
            # Obtener facturas para los lotes seleccionados con toda la información relacionada
            facturas_en_lotes = Factura.objects.filter(
                lote__id__in=selected_lotes_ids
            ).select_related(
                'ips', 'eps', 'paciente', 'contrato', 'lote', 'auditor'
            ).prefetch_related(
                'glosas', 'glosas__tipo_glosa', 'devolucion', 'devolucion__subcodigo'
            ).order_by('lote__nombre', 'numero')

    context = {
        'lotes': lotes,
        'facturas_en_lotes': facturas_en_lotes,
        'selected_lotes_ids': selected_lotes_ids,
        'valor_total_lotes': sum(f.valor_bruto for f in facturas_en_lotes),
        'total_facturas_lotes': len(facturas_en_lotes),
        'total_glosas_lotes': sum(f.glosas.count() for f in facturas_en_lotes),
        'valor_total_glosado_lotes': sum(g.valor_glosado for f in facturas_en_lotes for g in f.glosas.all()),
    }
    return render(request, 'auditoria/reportes/reporte_auditoria_lote.html', context)

@login_required
@role_required(['IPS', 'EPS'])
def lista_glosas(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    glosas = Glosa.objects.filter(factura=factura)
    return render(request, 'auditoria/lista_glosas.html', {'factura': factura, 'glosas': glosas})

@login_required
@role_required('IPS')
def responder_glosa(request, glosa_id):
    glosa = get_object_or_404(Glosa, id=glosa_id)
    
    # Verificar que la factura esté auditada y la glosa en un estado respondible
    if glosa.factura.estado != 'Auditada' or glosa.estado not in ['Pendiente', 'Devuelta a IPS']:
        messages.error(request, "No se puede responder esta glosa en el estado actual de la factura o glosa.")
        return redirect('auditoria:glosas_pendientes')

    tipos_respuesta = TipoGlosaRespuestaIPS.objects.all()
    subtipos_respuesta = SubtipoGlosaRespuestaIPS.objects.all() # Pasar subtipos para el select dinámico

    if request.method == 'POST':
        glosa.descripcion_respuesta = request.POST.get('descripcion_respuesta')
        glosa.tipo_glosa_respuesta_id = request.POST.get('tipo_glosa_respuesta')
        glosa.subtipo_glosa_respuesta_id = request.POST.get('subtipo_glosa_respuesta')
        
        if 'archivo_soporte_respuesta' in request.FILES:
            glosa.archivo_soporte_respuesta = request.FILES['archivo_soporte_respuesta']

        # La IPS indica si acepta o rechaza la glosa
        decision_ips = request.POST.get('decision_glosa')
        if decision_ips == 'true':
            glosa.aceptada = True
        elif decision_ips == 'false':
            glosa.aceptada = False
        else:
            glosa.aceptada = None # No definido por la IPS

        estado_anterior = glosa.estado
        glosa.estado = 'Respondida IPS' # Cambiar estado a respondida por IPS
        glosa.fecha_respuesta = timezone.now().date()
        glosa.save()
        
        # Registrar en el historial
        HistorialGlosa.registrar_cambio(
            glosa=glosa,
            accion='respondida_ips',
            usuario=request.user,
            estado_anterior=estado_anterior,
            estado_nuevo=glosa.estado,
            descripcion_cambio=f"Glosa respondida por IPS. Decisión: {'Aceptada' if glosa.aceptada else 'Rechazada' if glosa.aceptada == False else 'No definida'}",
            request=request
        )
        
        messages.success(request, "Respuesta a la glosa enviada exitosamente. Ahora está pendiente de decisión de la ET.")
        return redirect('auditoria:glosas_pendientes')

    context = {
        'glosa': glosa,
        'tipos_respuesta': tipos_respuesta,
        'subtipos_respuesta': subtipos_respuesta,
    }
    return render(request, 'auditoria/responder_glosa.html', context)


@login_required
@role_required(['ET', 'AUDITOR'])
def decidir_respuesta_glosa(request, glosa_id):
    glosa = get_object_or_404(Glosa, id=glosa_id)

    # Solo permitir decidir si la glosa está en estado Respondida IPS o Devuelta a IPS
    if glosa.estado not in ['Respondida IPS', 'Devuelta a IPS']:
        messages.error(request, "Esta glosa no está en un estado que requiera una decisión de la ET.")
        return redirect('auditoria:glosas_pendientes') # O la lista de glosas para ET

    if request.method == 'POST':
        decision_et = request.POST.get('decision_et')
        justificacion_et = request.POST.get('justificacion_et', '')
        valor_aceptado_et_input = request.POST.get('valor_aceptado_et')

        # Guardar estado anterior para el historial
        estado_anterior = glosa.estado
        valor_anterior = glosa.valor_aceptado_et

        if decision_et == 'aceptar_respuesta_ips':
            glosa.estado = 'Aceptada ET'
            glosa.valor_aceptado_et = Decimal('0.00') # ET acepta el rechazo de IPS, glosa se levanta, NO se descuenta del valor bruto
            accion_historial = 'decidida_et'
            descripcion_historial = "Respuesta de la IPS aceptada. Glosa levantada, se debe pagar."
            messages.success(request, "Respuesta de la IPS aceptada. Glosa levantada, se debe pagar.")
        elif decision_et == 'rechazar_respuesta_ips':
            glosa.estado = 'Rechazada ET'
            glosa.valor_aceptado_et = glosa.valor_glosado # ET rechaza el rechazo de IPS, glosa sigue válida, SÍ se descuenta del valor bruto
            accion_historial = 'decidida_et'
            descripcion_historial = "Respuesta de la IPS rechazada. Glosa válida, se descuenta del valor bruto."
            messages.warning(request, "Respuesta de la IPS rechazada. Glosa válida, se descuenta del valor bruto.")
        elif decision_et == 'devolver_a_ips':
            glosa.estado = 'Devuelta a IPS'
            glosa.valor_aceptado_et = None # Se reinicia el proceso de aceptación/rechazo
            accion_historial = 'devuelta_ips'
            descripcion_historial = "Glosa devuelta a la IPS para reevaluación."
            messages.info(request, "Glosa devuelta a la IPS para reevaluación.")
        else:
            messages.error(request, "Decisión de la ET no válida.")
            return redirect(request.META.get('HTTP_REFERER', 'auditoria:glosas_pendientes'))

        # Si se proporcionó un valor aceptado específico, úsalo
        if valor_aceptado_et_input:
            try:
                glosa.valor_aceptado_et = Decimal(valor_aceptado_et_input)
            except: # En caso de un valor inválido, no se modifica
                pass

        glosa.fecha_decision_et = timezone.now().date()
        glosa.decision_et_justificacion = justificacion_et
        
        glosa.save()
        
        # Actualizar la cuenta de cartera después de la decisión
        try:
            cuenta_cartera = glosa.factura.cuentacartera
            cuenta_cartera.actualizar_valores_glosas()
        except Exception as e:
            # Si hay error, crear cuenta de cartera básica
            from cartera.models import CuentaCartera
            CuentaCartera.objects.get_or_create(
                factura=glosa.factura,
                defaults={
                    'ips': glosa.factura.ips,
                    'eps': glosa.factura.eps,
                    'valor_inicial': glosa.factura.valor_bruto,
                    'valor_glosado_provisional': Decimal('0'),
                    'valor_glosado_definitivo': Decimal('0'),
                    'valor_pagable': glosa.factura.valor_bruto,
                    'valor_final': glosa.factura.valor_bruto,
                    'estado_pago': 'Pendiente'
                }
            )
            cuenta_cartera = glosa.factura.cuentacartera
            cuenta_cartera.actualizar_valores_glosas()
        
        # Registrar en el historial
        HistorialGlosa.registrar_cambio(
            glosa=glosa,
            accion=accion_historial,
            usuario=request.user,
            estado_anterior=estado_anterior,
            estado_nuevo=glosa.estado,
            valor_anterior=valor_anterior,
            valor_nuevo=glosa.valor_aceptado_et,
            descripcion_cambio=f"{descripcion_historial} Justificación: {justificacion_et}",
            request=request
        )
        
        return redirect('auditoria:glosas_pendientes') # Redirigir a una lista de glosas relevantes para la ET

    context = {
        'glosa': glosa,
    }
    return render(request, 'auditoria/decidir_respuesta_glosa.html', context)

@login_required
@role_required(['IPS', 'ET', 'AUDITOR'])
def historial_glosa(request, glosa_id):
    glosa = get_object_or_404(Glosa, id=glosa_id)
    
    # Verificar permisos: IPS solo puede ver sus propias glosas
    if request.user.profile.role == 'IPS' and glosa.ips != request.user.profile:
        messages.error(request, "No tiene permisos para ver el historial de esta glosa.")
        return redirect('auditoria:glosas_pendientes')
    
    # Obtener el historial ordenado por fecha
    historial = glosa.historial.all().select_related('usuario')
    
    context = {
        'glosa': glosa,
        'historial': historial,
    }
    return render(request, 'auditoria/historial_glosa.html', context)

@login_required
@role_required(['IPS', 'ET', 'AUDITOR'])
def glosas_pendientes(request):
    glosas = Glosa.objects.filter(estado__in=["Pendiente", "Respondida IPS", "Devuelta a IPS"]) # Mostrar glosas relevantes para IPS y ET
    if request.user.profile.role == 'IPS':
        glosas = glosas.filter(ips=request.user.profile)
    elif request.user.profile.role == 'EPS':
        glosas = glosas.filter(factura__eps=request.user.profile)
    elif request.user.profile.role == 'ET' or request.user.profile.role == 'AUDITOR':
        # ET/Auditor ve glosas que le competen decidir o las que están en proceso
        glosas = glosas.filter(factura__auditor=request.user).exclude(estado__in=['Aceptada ET', 'Rechazada ET', 'Indefinida']) # O ajusta el filtro según lo que quieras que vea el auditor/ET
        # Si la ET debe ver todas las glosas para decidir sobre ellas, el filtro cambia
        # Por ahora, se mostrarán las que aún no tienen una decisión final de la ET

    glosas = glosas.order_by('-fecha_glosa')
    return render(request, 'auditoria/glosas_pendientes.html', {'glosas': glosas})

@login_required
@role_required(['ET', 'AUDITOR'])
def lista_devoluciones(request):
    devoluciones = Devolucion.objects.select_related(
        'factura', 
        'factura__ips', 
        'subcodigo', 
        'subcodigo__codigo_padre',
        'devuelto_por'
    ).all()

    context = {
        'devoluciones': devoluciones,
        'title': 'Facturas Devueltas'
    }
    return render(request, 'auditoria/lista_devoluciones.html', context)

@login_required
@role_required(['ET', 'AUDITOR'])
def devolver_factura_manual(request, factura_id):
    # print(f"DEBUG: devolver_factura_manual entered. User authenticated: {request.user.is_authenticated}")
    # if request.user.is_authenticated and hasattr(request.user, 'profile'):
    #     print(f"DEBUG: User profile role: {request.user.profile.role}")
    # else:
    #     print("DEBUG: User not authenticated or profile not found.")

    if request.method == 'POST':
        factura = get_object_or_404(Factura, pk=factura_id)
        subcodigo_id = request.POST.get('subcodigo_devolucion')
        justificacion = request.POST.get('justificacion', '')

        if not subcodigo_id:
            messages.error(request, "Debe seleccionar un motivo de devolución.")
            return redirect('auditoria:lista_radicados')

        # Cambiar estado de la factura
        factura.estado = 'Devuelta'
        factura.save()

        # Crear el registro de devolución
        subcodigo_devolucion = get_object_or_404(SubcodigoDevolucion, pk=subcodigo_id)
        Devolucion.objects.create(
            factura=factura,
            subcodigo=subcodigo_devolucion,
            justificacion=justificacion,
            devuelto_por=request.user
        )

        messages.success(request, f"La factura {factura.numero} ha sido devuelta exitosamente.")
    
    return redirect('auditoria:lista_radicados')

@login_required
@role_required('IPS')
def mis_radicados(request):
    """
    Vista específica para IPS que muestra solo sus propios radicados
    """
    # Obtener solo las facturas de la IPS actual
    facturas = Factura.objects.filter(
        ips=request.user.profile
    ).select_related('ips', 'lote', 'auditor', 'paciente').order_by('-fecha_radicacion')

    # Contadores para la UI
    total_facturas = facturas.count()
    total_auditadas = facturas.filter(estado='Auditada').count()
    total_pendientes = facturas.exclude(estado='Auditada').count()
    total_con_glosas = facturas.filter(estado='Con Glosas').count()

    context = {
        'facturas': facturas,
        'total_facturas': total_facturas,
        'total_auditadas': total_auditadas,
        'total_pendientes': total_pendientes,
        'total_con_glosas': total_con_glosas,
    }
    
    return render(request, 'auditoria/mis_radicados.html', context)