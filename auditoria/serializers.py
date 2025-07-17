from rest_framework import serializers
from .models import SubtipoGlosa, SubCodigoGlosa, SubtipoGlosaRespuestaIPS

class SubtipoGlosaSerializer(serializers.ModelSerializer):
    codigo_nombre = serializers.SerializerMethodField()
    
    def get_codigo_nombre(self, obj):
        return f"{obj.codigo} - {obj.nombre}"
    
    class Meta:
        model = SubtipoGlosa
        fields = ['pk', 'nombre', 'codigo', 'codigo_nombre']

class SubCodigoGlosaSerializer(serializers.ModelSerializer):
    codigo_nombre = serializers.SerializerMethodField()
    
    def get_codigo_nombre(self, obj):
        return f"{obj.codigo} - {obj.nombre}"
    
    class Meta:
        model = SubCodigoGlosa
        fields = ['pk', 'nombre', 'codigo', 'codigo_nombre']

class SubtipoGlosaRespuestaIPSSerializer(serializers.ModelSerializer):
    codigo_nombre = serializers.SerializerMethodField()
    
    def get_codigo_nombre(self, obj):
        return f"{obj.codigo} - {obj.nombre}"
    
    class Meta:
        model = SubtipoGlosaRespuestaIPS
        fields = ['pk', 'nombre', 'codigo', 'codigo_nombre'] 