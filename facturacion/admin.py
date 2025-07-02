from django.contrib import admin
from .models import Factura, Paciente, Contrato, RipsConsulta, RipsMedicamento, RipsProcedimiento, RipsHospitalizacion, RipsOtroServicio

admin.site.register(Factura)
admin.site.register(Paciente)
admin.site.register(Contrato)
admin.site.register(RipsConsulta)
admin.site.register(RipsMedicamento)
admin.site.register(RipsProcedimiento)
admin.site.register(RipsHospitalizacion)
admin.site.register(RipsOtroServicio)