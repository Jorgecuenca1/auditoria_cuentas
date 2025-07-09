from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from facturacion.models import Factura, Paciente, RipsConsulta, RipsMedicamento, RipsProcedimiento, RipsHospitalizacion, RipsOtroServicio, Devolucion, CodigoDevolucion, SubcodigoDevolucion
from .models import Glosa, TipoGlosa, SubtipoGlosa, SubCodigoGlosa, TipoGlosaRespuestaIPS, SubtipoGlosaRespuestaIPS
from .forms import TipoAuditoriaForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum, Count, F, Case, When, Value, CharField
from accounts.decorators import role_required

@login_required
@role_required('ET')
def reporte_glosas(request):
    # Estadísticas generales de glosas
    total_glosas = Glosa.objects.count()
    glosas_pendientes = Glosa.objects.filter(estado="Pendiente").count()
    glosas_respondidas = Glosa.objects.filter(estado="Respondida").count()
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

from .models import Factura
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404

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

from functools import wraps
from django.shortcuts import redirect

def role_required(*allowed_roles):
    """
    Decorator que permite acceso solo si request.user.profile.role
    está dentro de allowed_roles.
    Uso:
      @role_required('ET', 'AUDITOR')
    """
    def decorator(view_fn):
        @wraps(view_fn)
        def _wrapped(request, *args, **kwargs):
            user_role = getattr(request.user, 'profile', None) and request.user.profile.role
            if user_role not in allowed_roles:
                return redirect('accounts:forbidden')  # o a donde quieras
            return view_fn(request, *args, **kwargs)
        return _wrapped
    return decorator

@login_required
@role_required('ET','AUDITOR')
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
            glosas_pendientes = Glosa.objects.filter(factura=factura, estado="Pendiente").exists()
            if glosas_pendientes:
                messages.error(request, "No se puede finalizar la auditoría mientras haya glosas pendientes por responder.")
            else:
                factura.estado = 'Auditada'
                factura.save()
                messages.success(request, "Auditoría finalizada exitosamente.")
                return redirect('auditoria:lista_radicados')
        else:
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
            if item_type == 'consulta' and item_pk:
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
            if related_item and hasattr(related_item, 'paciente'):
                glosa_kwargs['paciente'] = related_item.paciente
            else:
                messages.warning(request, "Glosa creada sin asociación a un ítem RIPS específico o paciente.")
            # Asignar la IPS de la factura a la glosa
            glosa_kwargs['ips'] = factura.ips
            Glosa.objects.create(**glosa_kwargs)
            messages.success(request, "Glosa creada exitosamente.")
            return redirect('auditoria:auditar_factura', factura_id=factura.id)
    
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
@role_required('ET', 'AUDITOR')
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
    ).order_by('fecha_glosa')

    rips_consultas = RipsConsulta.objects.filter(factura=factura)
    rips_medicamentos = RipsMedicamento.objects.filter(factura=factura)
    rips_procedimientos = RipsProcedimiento.objects.filter(factura=factura)
    rips_hospitalizaciones = RipsHospitalizacion.objects.filter(factura=factura)
    rips_otros_servicios = RipsOtroServicio.objects.filter(factura=factura)

    context = {
        'factura': factura,
        'paciente': factura.paciente,
        'glosas': glosas,
        'rips_consultas': rips_consultas,
        'rips_medicamentos': rips_medicamentos,
        'rips_procedimientos': rips_procedimientos,
        'rips_hospitalizaciones': rips_hospitalizaciones,
        'rips_otros_servicios': rips_otros_servicios,
    }

    return render(request, 'auditoria/reportes/reporte_auditoria_detalle.html', context)

@login_required
@role_required('ET')
def reporte_auditoria_lote(request):
    from facturacion.models import Lote # Import Lote model here

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
    tipos_respuesta = TipoGlosaRespuestaIPS.objects.all()

    if request.method == 'POST':
        glosa.descripcion_respuesta = request.POST.get('descripcion_respuesta')
        glosa.tipo_glosa_respuesta_id = request.POST.get('tipo_glosa_respuesta')
        glosa.subtipo_glosa_respuesta_id = request.POST.get('subtipo_glosa_respuesta')
        
        if 'archivo_soporte_respuesta' in request.FILES:
            glosa.archivo_soporte_respuesta = request.FILES['archivo_soporte_respuesta']

        # Lógica para la decisión de la glosa por el rol 'IPS'
        if request.user.profile.role == 'IPS':
            decision = request.POST.get('decision_glosa')
            if decision == 'true':
                glosa.aceptada = True
                glosa.estado = 'Aceptada'
            elif decision == 'false':
                glosa.aceptada = False
                glosa.estado = 'Rechazada'
            else:
                glosa.aceptada = None # Se mantiene como respondida pero sin decisión final
                glosa.estado = 'Respondida'
        else: 
            glosa.estado = 'Respondida'

        glosa.fecha_respuesta = timezone.now().date()
        glosa.save()
        
        messages.success(request, "Respuesta a la glosa enviada exitosamente.")
        return redirect('auditoria:glosas_pendientes')

    return render(request, 'auditoria/responder_glosa.html', {
        'glosa': glosa,
        'tipos_respuesta': tipos_respuesta,
    })

@login_required
@role_required('IPS')
def glosas_pendientes(request):
    glosas = Glosa.objects.filter(estado="Pendiente")
    if request.user.profile.role == 'IPS':
        glosas = glosas.filter(ips=request.user.profile)
    elif request.user.profile.role == 'EPS':
        glosas = glosas.filter(factura__eps=request.user.profile)
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
    print(f"DEBUG: devolver_factura_manual entered. User authenticated: {request.user.is_authenticated}")
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        print(f"DEBUG: User profile role: {request.user.profile.role}")
    else:
        print("DEBUG: User not authenticated or profile not found.")

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