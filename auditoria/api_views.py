from rest_framework import generics
from .models import SubtipoGlosa, SubCodigoGlosa, SubtipoGlosaRespuestaIPS
from .serializers import SubtipoGlosaSerializer, SubCodigoGlosaSerializer, SubtipoGlosaRespuestaIPSSerializer

class SubtipoGlosaListView(generics.ListAPIView):
    serializer_class = SubtipoGlosaSerializer

    def get_queryset(self):
        tipo_glosa_id = self.kwargs.get('tipo_glosa_id')
        return SubtipoGlosa.objects.filter(tipo_glosa_id=tipo_glosa_id)

class SubCodigoGlosaListView(generics.ListAPIView):
    serializer_class = SubCodigoGlosaSerializer

    def get_queryset(self):
        subtipo_glosa_id = self.kwargs.get('subtipo_glosa_id')
        return SubCodigoGlosa.objects.filter(subtipo_glosa_id=subtipo_glosa_id)

class SubtipoGlosaRespuestaIPSListView(generics.ListAPIView):
    serializer_class = SubtipoGlosaRespuestaIPSSerializer

    def get_queryset(self):
        tipo_glosa_respuesta_id = self.kwargs.get('tipo_glosa_respuesta_id')
        return SubtipoGlosaRespuestaIPS.objects.filter(tipo_glosa_respuesta_id=tipo_glosa_respuesta_id) 