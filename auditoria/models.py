from django.db import models
from facturacion.models import Factura, Paciente, RipsConsulta, RipsMedicamento, RipsProcedimiento, RipsHospitalizacion, RipsOtroServicio
from accounts.models import Profile

class TipoGlosa(models.Model):
    codigo = models.CharField(max_length=10)
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
        return f"{self.tipo_glosa.codigo} {self.codigo} - {self.nombre}"

class SubCodigoGlosa(models.Model):
    subtipo_glosa = models.ForeignKey(SubtipoGlosa, on_delete=models.CASCADE, related_name='subcodigos')
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=255)

    class Meta:
        unique_together = ('subtipo_glosa', 'codigo')

    def __str__(self):
        return f"{self.subtipo_glosa.tipo_glosa.codigo}{self.subtipo_glosa.codigo}{self.codigo} - {self.nombre}"

class TipoGlosaRespuestaIPS(models.Model):
    codigo = models.CharField(max_length=10)
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
    ips = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.SET_NULL, limit_choices_to={'role': 'IPS'})
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
    
    ESTADO_GLOSA_CHOICES = [
        ("Pendiente", "Pendiente de Respuesta IPS"),
        ("Respondida IPS", "Respondida por IPS"),
        ("Aceptada ET", "Aceptada por ET"),
        ("Rechazada ET", "Rechazada por ET"),
        ("Devuelta a IPS", "Devuelta a IPS (Reevaluación)"),
        ("Indefinida", "Glosa Indefinida"),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_GLOSA_CHOICES, default="Pendiente")
    fecha_glosa = models.DateField(auto_now_add=True)

    # Campos para la respuesta de la glosa por parte de la IPS
    descripcion_respuesta = models.TextField(blank=True, null=True)
    archivo_soporte_respuesta = models.FileField(upload_to='respuestas_glosas/', blank=True, null=True)
    tipo_glosa_respuesta = models.ForeignKey(TipoGlosaRespuestaIPS, on_delete=models.SET_NULL, null=True, blank=True)
    subtipo_glosa_respuesta = models.ForeignKey(SubtipoGlosaRespuestaIPS, on_delete=models.SET_NULL, null=True, blank=True)
    
    aceptada = models.BooleanField(null=True, blank=True, help_text="Indica si la IPS aceptó la glosa (True) o la rechazó (False).")
    fecha_respuesta = models.DateField(null=True, blank=True)

    # Campos para la decisión de la ET sobre la respuesta de la IPS
    fecha_decision_et = models.DateField(null=True, blank=True)
    valor_aceptado_et = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Valor de la glosa que se descuenta del valor bruto. Si es 0, la glosa se levanta y no se descuenta.")
    decision_et_justificacion = models.TextField(blank=True, null=True, help_text="Justificación de la decisión de la ET o motivo de la devolución.")

    def __str__(self):
        return f"Glosa {self.id} a factura {self.factura.numero}"

class HistorialGlosa(models.Model):
    glosa = models.ForeignKey(Glosa, on_delete=models.CASCADE, related_name='historial')
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, help_text="Usuario que realizó el cambio")
    
    # Información del cambio
    ACCION_CHOICES = [
        ('creada', 'Glosa Creada'),
        ('estado_cambiado', 'Estado Cambiado'),
        ('respondida_ips', 'Respondida por IPS'),
        ('decidida_et', 'Decidida por ET'),
        ('devuelta_ips', 'Devuelta a IPS'),
        ('archivo_adjuntado', 'Archivo Adjuntado'),
        ('valor_modificado', 'Valor Modificado'),
        ('justificacion_agregada', 'Justificación Agregada'),
    ]
    accion = models.CharField(max_length=50, choices=ACCION_CHOICES)
    
    # Detalles del cambio
    estado_anterior = models.CharField(max_length=20, blank=True, null=True)
    estado_nuevo = models.CharField(max_length=20, blank=True, null=True)
    valor_anterior = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    valor_nuevo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    descripcion_cambio = models.TextField(blank=True, null=True)
    
    # Información adicional
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha_cambio']
        verbose_name = "Historial de Glosa"
        verbose_name_plural = "Historial de Glosas"
    
    def __str__(self):
        return f"Historial {self.id} - Glosa {self.glosa.id} - {self.get_accion_display()} - {self.fecha_cambio.strftime('%Y-%m-%d %H:%M')}"
    
    @classmethod
    def registrar_cambio(cls, glosa, accion, usuario=None, estado_anterior=None, estado_nuevo=None, 
                        valor_anterior=None, valor_nuevo=None, descripcion_cambio=None, 
                        request=None):
        """
        Método de clase para registrar cambios en el historial de una glosa
        """
        historial = cls(
            glosa=glosa,
            usuario=usuario,
            accion=accion,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            valor_anterior=valor_anterior,
            valor_nuevo=valor_nuevo,
            descripcion_cambio=descripcion_cambio
        )
        
        # Capturar información del request si está disponible
        if request:
            historial.ip_address = cls.get_client_ip(request)
            historial.user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        historial.save()
        return historial
    
    @staticmethod
    def get_client_ip(request):
        """Obtiene la IP del cliente desde el request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
