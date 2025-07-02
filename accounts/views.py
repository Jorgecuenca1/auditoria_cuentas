from .models import Profile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from .forms import UserForm, ProfileForm
from .decorators import role_required

@login_required
def profile_view(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})

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
