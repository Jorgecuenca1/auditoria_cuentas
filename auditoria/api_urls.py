from django.urls import path
from . import api_views

app_name = 'auditoria_api'

urlpatterns = [
    path('subtipos/<int:tipo_glosa_id>/', api_views.SubtipoGlosaListView.as_view(), name='subtipo-list'),
    path('subcodigos/<int:subtipo_glosa_id>/', api_views.SubCodigoGlosaListView.as_view(), name='subcodigo-list'),
    path('subtipos_respuesta/<int:tipo_glosa_respuesta_id>/', api_views.SubtipoGlosaRespuestaIPSListView.as_view(), name='subtipo-respuesta-list'),
] 