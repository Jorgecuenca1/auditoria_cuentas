from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from facturacion.models import Factura, Paciente, RipsConsulta, RipsMedicamento, RipsProcedimiento, RipsHospitalizacion, RipsOtroServicio
from .models import Glosa, TipoGlosa, SubtipoGlosa, SubCodigoGlosa, TipoGlosaRespuestaIPS, SubtipoGlosaRespuestaIPS
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
        'estado_auditoria'
    ).annotate(
        total_facturas=Count('id'),
        valor_total=Sum('valor_bruto')
    ).order_by('estado_auditoria')

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
    total_auditadas = facturas.filter(estado_auditoria='Finalizada').count()
    total_pendientes = facturas.exclude(estado_auditoria='Finalizada').count()
    
    # Auditorías por IPS
    auditorias_por_ips = facturas.values(
        'ips__entidad_nombre',
        'estado_auditoria'
    ).annotate(
        total=Count('id'),
        valor_total=Sum('valor_bruto')
    ).order_by('ips__entidad_nombre', 'estado_auditoria')

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
    # Proceso de asignación por parte de la ET
    if request.method == 'POST' and request.user.profile.role == 'ET':
        factura_id = request.POST.get('factura_id')
        auditor_id = request.POST.get('auditor_id')
        factura = get_object_or_404(Factura, pk=factura_id)
        auditor = get_object_or_404(User, pk=auditor_id, profile__role='AUDITOR')
        factura.auditor = auditor
        factura.save()
        messages.success(request, f'Auditor "{auditor.get_full_name() or auditor.username}" asignado a la factura {factura.numero}.')
        return redirect('auditoria:lista_radicados')

    # Filtrado según rol
    if request.user.profile.role == 'AUDITOR':
        facturas = Factura.objects.filter(auditor=request.user)
    else:  # ET
        facturas = Factura.objects.all()

    # Solo los usuarios con role AUDITOR para poblar el <select>
    auditores = User.objects.filter(profile__role='AUDITOR')

    return render(request, 'auditoria/lista_radicados.html', {
        'facturas': facturas,
        'auditores': auditores,
    })
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
                factura.estado_auditoria = 'Finalizada'
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
            Glosa.objects.create(**glosa_kwargs)
            messages.success(request, "Glosa creada exitosamente.")
            return redirect('auditoria:auditar_factura', factura_id=factura.id)
    
    glosas = Glosa.objects.filter(factura=factura)
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
@role_required(['IPS', 'EPS'])
def lista_glosas(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    glosas = Glosa.objects.filter(factura=factura)
    return render(request, 'auditoria/lista_glosas.html', {'factura': factura, 'glosas': glosas})

@login_required
@role_required(['IPS', 'EPS'])
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
@role_required(['IPS', 'EPS'])
def glosas_pendientes(request):
    glosas = Glosa.objects.filter(estado="Pendiente")
    if request.user.profile.role == 'IPS':
        glosas = glosas.filter(factura__ips=request.user.profile)
    elif request.user.profile.role == 'EPS':
        glosas = glosas.filter(factura__eps=request.user.profile)
    
    glosas = glosas.order_by('-fecha_glosa')
    return render(request, 'auditoria/glosas_pendientes.html', {'glosas': glosas})