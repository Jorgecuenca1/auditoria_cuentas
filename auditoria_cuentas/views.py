from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def error_403(request, exception=None):
    return render(request, '403.html', status=403)

def landing_page(request):
    return render(request, 'landing.html')

@login_required
def dashboard_view(request):
    # Lógica para el dashboard, que podría variar según el rol del usuario
    context = {
        'user_role': request.user.profile.role if hasattr(request.user, 'profile') else 'N/A',
        'username': request.user.username,
    }
    return render(request, 'dashboard.html', context) 