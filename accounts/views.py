from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.http import JsonResponse

from .models import Profile
from .forms import UserForm, ProfileForm
from .decorators import role_required
from facturacion.models import Factura, Lote, Contrato
from auditoria.models import Glosa

@login_required
def profile_view(request):
    profile = Profile.objects.get(user=request.user)
    notifications = []
    today = timezone.now().date()

    if profile.role == 'AUDITOR':
        # Alertas para facturas pendientes de auditoría (20 días)
        auditoria_deadline = today + timedelta(days=20)
        pending_invoices = Factura.objects.filter(
            auditor=request.user,
            estado='Radicada',
            fecha_radicacion__lte=auditoria_deadline
        ).order_by('fecha_radicacion')

        for invoice in pending_invoices:
            days_left = (invoice.fecha_radicacion - today).days
            if days_left <= 20:
                notifications.append({
                    'message': f'Tienes una factura pendiente de auditoría (No. {invoice.numero}) con fecha de radicación {invoice.fecha_radicacion.strftime("%Y-%m-%d")}. Fecha límite: {auditoria_deadline.strftime("%Y-%m-%d")}.',
                    'url': f'/auditoria/factura/{invoice.pk}/'
                })

    if profile.role == 'ET':
        # Alertas para facturas pendientes de auditoría (20 días) para todos los auditores
        auditoria_deadline = today + timedelta(days=20)
        pending_invoices_et = Factura.objects.filter(
            estado='Radicada',
            fecha_radicacion__lte=auditoria_deadline
        ).order_by('fecha_radicacion')

        for invoice in pending_invoices_et:
            days_left = (invoice.fecha_radicacion - today).days
            if days_left <= 20:
                auditor_name = invoice.auditor.username if invoice.auditor else "(Sin asignar)"
                notifications.append({
                    'message': f'Factura pendiente de auditoría (No. {invoice.numero}) asignada a {auditor_name} con fecha de radicación {invoice.fecha_radicacion.strftime("%Y-%m-%d")}. Fecha límite: {auditoria_deadline.strftime("%Y-%m-%d")}.',
                    'url': f'/auditoria/factura/{invoice.pk}/'
                })

    if profile.role == 'IPS':
        # Alertas para glosas pendientes de respuesta (3 días)
        response_deadline = today + timedelta(days=3)
        pending_glosas = Glosa.objects.filter(
            ips=profile,
            estado='Pendiente',
            fecha_glosa__lte=response_deadline
        ).order_by('fecha_glosa')

        for glosa in pending_glosas:
            days_left = (glosa.fecha_glosa - today).days
            if days_left <= 3:
                notifications.append({
                    'message': f'Tienes una glosa pendiente de respuesta para la factura No. {glosa.factura.numero} (solo tienes 3 días para responder). Fecha de glosa: {glosa.fecha_glosa.strftime("%Y-%m-%d")}.',
                    'url': f'/auditoria/responder-glosa/{glosa.pk}/'
                })
    
    context = {
        'profile': profile,
        'notifications': notifications,
        'notifications_count': len(notifications)
    }

    return render(request, 'accounts/profile.html', context)

@login_required
@role_required('ADMIN')
def user_list(request):
    users = User.objects.all().select_related('profile')
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
@role_required('ADMIN')
@transaction.atomic
def user_create(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, "Usuario y perfil creados exitosamente.")
            return redirect('accounts:user_list')
    else:
        user_form = UserForm()
        profile_form = ProfileForm()
    return render(request, 'accounts/user_form.html', {'user_form': user_form, 'profile_form': profile_form, 'title': 'Crear Usuario'})

@login_required
@role_required('ADMIN')
@transaction.atomic
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile = get_object_or_404(Profile, user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            # Solo actualizar la contraseña si se proporciona una nueva
            if user_form.cleaned_data['password']:
                user.set_password(user_form.cleaned_data['password'])
            user_form.save()
            profile_form.save()
            messages.success(request, "Usuario y perfil actualizados exitosamente.")
            return redirect('accounts:user_list')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)
    return render(request, 'accounts/user_form.html', {'user_form': user_form, 'profile_form': profile_form, 'title': 'Editar Usuario'})

@login_required
def forbidden(request):
    return render(request, '403.html', {})

@login_required
def dashboard_counts(request):
    counts = {
        'contratos': Contrato.objects.count(),
        'lotes': Lote.objects.count(),
        'facturas_radicadas': Factura.objects.filter(estado='Radicada').count(),
        'glosas_pendientes': Glosa.objects.filter(estado='Pendiente').count(),
        'usuarios': User.objects.count(),
        'perfiles_ips': Profile.objects.filter(role='IPS').count(),
        'total_facturas': Factura.objects.count(),
        'facturas_por_estado': list(Factura.objects.values('estado').annotate(count=Count('id'))),
    }
    return JsonResponse(counts)
