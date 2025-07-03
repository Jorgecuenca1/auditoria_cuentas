from rest_framework import serializers
from .models import SubtipoGlosa, SubCodigoGlosa, SubtipoGlosaRespuestaIPS

class SubtipoGlosaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubtipoGlosa
        fields = ['pk', 'nombre']

class SubCodigoGlosaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCodigoGlosa
        fields = ['pk', 'nombre']

class SubtipoGlosaRespuestaIPSSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubtipoGlosaRespuestaIPS
        fields = ['pk', 'nombre'] 