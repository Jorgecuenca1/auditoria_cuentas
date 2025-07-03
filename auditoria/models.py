from django.db import models
from facturacion.models import Factura, Paciente, RipsConsulta, RipsMedicamento, RipsProcedimiento, RipsHospitalizacion, RipsOtroServicio
from accounts.models import Profile

class TipoGlosa(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class SubtipoGlosa(models.Model):
    tipo_glosa = models.ForeignKey(TipoGlosa, on_delete=models.CASCADE, related_name='subtipos')
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=255)

    class Meta:
        unique_together = ('tipo_glosa', 'codigo')

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class SubCodigoGlosa(models.Model):
    subtipo_glosa = models.ForeignKey(SubtipoGlosa, on_delete=models.CASCADE, related_name='subcodigos')
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=255)

    class Meta:
        unique_together = ('subtipo_glosa', 'codigo')

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class TipoGlosaRespuestaIPS(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class SubtipoGlosaRespuestaIPS(models.Model):
    tipo_glosa_respuesta = models.ForeignKey(TipoGlosaRespuestaIPS, on_delete=models.CASCADE, related_name='subtipos_respuesta')
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Glosa(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='glosas')
    paciente = models.ForeignKey(Paciente, on_delete=models.SET_NULL, null=True, blank=True)
    consulta = models.ForeignKey(RipsConsulta, on_delete=models.SET_NULL, null=True, blank=True, related_name='glosas')
    medicamento = models.ForeignKey(RipsMedicamento, on_delete=models.SET_NULL, null=True, blank=True, related_name='glosas')
    procedimiento = models.ForeignKey(RipsProcedimiento, on_delete=models.SET_NULL, null=True, blank=True, related_name='glosas')
    hospitalizacion = models.ForeignKey(RipsHospitalizacion, on_delete=models.SET_NULL, null=True, blank=True, related_name='glosas')
    otro_servicio = models.ForeignKey(RipsOtroServicio, on_delete=models.SET_NULL, null=True, blank=True, related_name='glosas')

    # Campos para la creación de la glosa
    tipo_glosa = models.ForeignKey(TipoGlosa, on_delete=models.PROTECT, null=True, blank=True)
    subtipo_glosa = models.ForeignKey(SubtipoGlosa, on_delete=models.PROTECT, null=True, blank=True)
    subcodigo_glosa = models.ForeignKey(SubCodigoGlosa, on_delete=models.PROTECT, null=True, blank=True)
    
    descripcion = models.TextField()
    valor_glosado = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20, default="Pendiente")
    fecha_glosa = models.DateField(auto_now_add=True)

    # Campos para la respuesta de la glosa por parte de la IPS
    descripcion_respuesta = models.TextField(blank=True, null=True)
    archivo_soporte_respuesta = models.FileField(upload_to='respuestas_glosas/', blank=True, null=True)
    tipo_glosa_respuesta = models.ForeignKey(TipoGlosaRespuestaIPS, on_delete=models.SET_NULL, null=True, blank=True)
    subtipo_glosa_respuesta = models.ForeignKey(SubtipoGlosaRespuestaIPS, on_delete=models.SET_NULL, null=True, blank=True)
    
    aceptada = models.BooleanField(null=True, blank=True)
    fecha_respuesta = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Glosa {self.id} a factura {self.factura.numero}"
