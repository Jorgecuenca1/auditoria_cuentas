from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.urls import reverse

def role_required(allowed_roles):
    """
    Decorador que verifica si el usuario tiene uno de los roles permitidos.
    allowed_roles puede ser una lista de roles o un solo rol.
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]
        
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Debe iniciar sesión para acceder a esta página.")
                return redirect('accounts:login')
            
            if not hasattr(request.user, 'profile'):
                messages.error(request, "El usuario no tiene un perfil asociado.")
                return redirect('accounts:login')
                
            if request.user.profile.role not in allowed_roles:
                messages.error(request, "No tiene permisos para acceder a esta página.")
                return redirect(reverse('accounts:forbidden'))
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator 