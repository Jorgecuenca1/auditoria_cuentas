from django.shortcuts import render, redirect, get_object_or_404
from facturacion.models import Factura, RipsItem
from .models import Glosa
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum, Count
from accounts.decorators import role_required

@login_required
@role_required('ET')
def reporte_glosas(request):
    # Estadísticas generales de glosas
    total_glosas = Glosa.objects.count()
    glosas_pendientes = Glosa.objects.filter(estado="Pendiente").count()
    glosas_respondidas = Glosa.objects.filter(estado="Respondida").count()
    valor_total_glosado = Glosa.objects.aggregate(total=Sum('valor_glosado'))['total'] or 0

    # Glosas por IPS
    glosas_por_ips = Glosa.objects.values(
        'factura__ips'
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
        'ips'
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
        'ips',
        'estado_auditoria'
    ).annotate(
        total=Count('id'),
        valor_total=Sum('valor_bruto')
    ).order_by('ips', 'estado_auditoria')

    return render(request, 'auditoria/reportes/reporte_auditorias.html', {
        'total_auditadas': total_auditadas,
        'total_pendientes': total_pendientes,
        'auditorias_por_ips': auditorias_por_ips,
    })

@login_required
@role_required('ET')
def lista_radicados(request):
    facturas = Factura.objects.all()
    return render(request, 'auditoria/lista_radicados.html', {'facturas': facturas})

@login_required
@role_required('ET')
def auditar_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    items = RipsItem.objects.filter(factura=factura)
    # Extraer paciente_id únicos
    identificaciones = sorted(set(item.paciente_id for item in items if item.paciente_id))
    
    if request.method == 'POST':
        if 'finalizar_auditoria' in request.POST:
            # Verificar si hay glosas pendientes
            glosas_pendientes = Glosa.objects.filter(factura=factura, estado="Pendiente").exists()
            if glosas_pendientes:
                messages.error(request, "No se puede finalizar la auditoría mientras haya glosas pendientes por responder.")
            else:
                factura.estado_auditoria = 'Finalizada'
                factura.save()
                messages.success(request, "Auditoría finalizada exitosamente.")
                return redirect('auditoria:lista_radicados')
        else:
            # Lógica existente para crear glosas
            item_id = request.POST.get('item_id')
            codigo_glosa = request.POST.get('codigo_glosa')
            descripcion = request.POST.get('descripcion')
            valor_glosado = request.POST.get('valor_glosado')
            Glosa.objects.create(
                factura=factura,
                item_id=item_id,
                codigo_glosa=codigo_glosa,
                descripcion=descripcion,
                valor_glosado=valor_glosado
            )
    
    glosas = Glosa.objects.filter(factura=factura)
    return render(request, 'auditoria/auditar_factura.html', {
        'factura': factura,
        'items': items,
        'glosas': glosas,
        'identificaciones': identificaciones,
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
    if request.method == 'POST':
        respuesta = request.POST.get('respuesta')
        glosa.respuesta = respuesta
        glosa.estado = 'Respondida'
        glosa.fecha_respuesta = timezone.now().date()
        glosa.save()
        return redirect('auditoria:lista_glosas', factura_id=glosa.factura.id)
    return render(request, 'auditoria/responder_glosa.html', {'glosa': glosa})

@login_required
@role_required(['IPS', 'EPS'])
def glosas_pendientes(request):
    # Filtrar glosas según el rol del usuario
    glosas = Glosa.objects.filter(estado="Pendiente")
    if request.user.profile.role == 'IPS':
        # Si es IPS, solo ver sus propias glosas
        glosas = glosas.filter(factura__ips=request.user.profile)
    elif request.user.profile.role == 'EPS':
        # Si es EPS, solo ver las glosas de su entidad
        glosas = glosas.filter(factura__eps=request.user.profile)
    
    glosas = glosas.order_by('-fecha_glosa')
    return render(request, 'auditoria/glosas_pendientes.html', {'glosas': glosas})