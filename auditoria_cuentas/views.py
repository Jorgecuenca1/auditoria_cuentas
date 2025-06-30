from django.shortcuts import render

def error_403(request, exception=None):
    return render(request, '403.html', status=403)

def landing_page(request):
    return render(request, 'landing.html') 