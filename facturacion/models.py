from django.db import models
from accounts.models import Profile
from django.contrib.auth.models import User

class Contrato(models.Model):
    numero = models.CharField(max_length=50)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    tipo = models.CharField(max_length=50)
    servicios_cubiertos = models.TextField(blank=True, null=True)
    tarifario_adjunto = models.FileField(upload_to='tarifarios/', blank=True, null=True, help_text="Adjunto del tarifario general asociado a este contrato")
    condiciones_pago = models.TextField(blank=True, null=True)
    adjunto = models.FileField(upload_to='contratos/', blank=True, null=True, help_text="Adjunto del contrato completo")
    alerta_vencimiento = models.BooleanField(default=False)
    def __str__(self):
        return f"Contrato {self.numero} ({self.tipo})"

class Paciente(models.Model):
    tipo_documento = models.CharField(max_length=5)
    numero_documento = models.CharField(max_length=20)
    tipo_usuario = models.CharField(max_length=2)  # 11, 12, etc.
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=1)
    pais_residencia = models.CharField(max_length=5)
    municipio_residencia = models.CharField(max_length=10)
    zona_territorial = models.CharField(max_length=2)
    incapacidad = models.CharField(max_length=2, blank=True, null=True)
    pais_origen = models.CharField(max_length=5, blank=True, null=True)
    # Puedes agregar más campos según el RIPS
    def __str__(self):
        return f"{self.tipo_documento} {self.numero_documento}"

class Factura(models.Model):
    numero = models.CharField(max_length=50)
    cufe = models.CharField(max_length=150)
    fecha_emision = models.DateField()
    fecha_radicacion = models.DateField(auto_now_add=True)
    ips = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='facturas_ips')
    eps = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='facturas_eps')
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, null=True, blank=True)
    valor_bruto = models.DecimalField(max_digits=12, decimal_places=2)
    estado_auditoria = models.CharField(max_length=20, default="Radicada")
    archivo_rips = models.FileField(upload_to='rips/')
    contrato = models.ForeignKey('Contrato', on_delete=models.SET_NULL, null=True, blank=True)
    auditor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='facturas_auditadas',
        limit_choices_to={'profile__role': 'AUDITOR'}
    )
    def __str__(self):
        return f"Factura {self.numero} CUFE {self.cufe}"

class RipsConsulta(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    cod_prestador = models.CharField(max_length=20)
    fecha_inicio_atencion = models.DateTimeField()
    num_autorizacion = models.CharField(max_length=20)
    cod_consulta = models.CharField(max_length=20)  # FK a CUPS
    modalidad_grupo_servicio = models.CharField(max_length=2)
    grupo_servicios = models.CharField(max_length=5)
    cod_servicio = models.CharField(max_length=10)
    finalidad_tecnologia = models.CharField(max_length=5)
    causa_motivo_atencion = models.CharField(max_length=5)
    cod_diagnostico_principal = models.CharField(max_length=10)  # FK a CIE10
    tipo_diagnostico_principal = models.CharField(max_length=2)
    vr_servicio = models.DecimalField(max_digits=12, decimal_places=2)
    concepto_recaudo = models.CharField(max_length=5)
    valor_pago_moderador = models.DecimalField(max_digits=12, decimal_places=2)
    consecutivo = models.IntegerField()
    # ...otros campos según RIPS

class RipsMedicamento(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    cod_prestador = models.CharField(max_length=20)
    num_autorizacion = models.CharField(max_length=20)
    id_mipres = models.CharField(max_length=20, blank=True, null=True)
    fecha_dispensacion = models.DateTimeField()
    cod_diagnostico_principal = models.CharField(max_length=10)
    tipo_medicamento = models.CharField(max_length=2)
    cod_tecnologia_salud = models.CharField(max_length=20)  # FK a CUMS
    nom_tecnologia_salud = models.CharField(max_length=255, blank=True, null=True)
    concentracion_medicamento = models.CharField(max_length=50, blank=True, null=True)
    unidad_medida = models.CharField(max_length=10, blank=True, null=True)
    forma_farmaceutica = models.CharField(max_length=50, blank=True, null=True)
    unidad_min_dispensa = models.IntegerField()
    cantidad_medicamento = models.IntegerField()
    dias_tratamiento = models.IntegerField()
    vr_unit_medicamento = models.DecimalField(max_digits=12, decimal_places=2)
    vr_servicio = models.DecimalField(max_digits=12, decimal_places=2)
    concepto_recaudo = models.CharField(max_length=5)
    valor_pago_moderador = models.DecimalField(max_digits=12, decimal_places=2)
    consecutivo = models.IntegerField()
    # ...otros campos según RIPS

class RipsProcedimiento(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    cod_prestador = models.CharField(max_length=20)
    fecha_inicio_atencion = models.DateTimeField()
    num_autorizacion = models.CharField(max_length=20)
    cod_procedimiento = models.CharField(max_length=20)  # FK a CUPS
    via_ingreso_servicio = models.CharField(max_length=5)
    modalidad_grupo_servicio = models.CharField(max_length=2)
    grupo_servicios = models.CharField(max_length=5)
    cod_servicio = models.CharField(max_length=10)
    finalidad_tecnologia = models.CharField(max_length=5)
    cod_diagnostico_principal = models.CharField(max_length=10)
    vr_servicio = models.DecimalField(max_digits=12, decimal_places=2)
    concepto_recaudo = models.CharField(max_length=5)
    valor_pago_moderador = models.DecimalField(max_digits=12, decimal_places=2)
    consecutivo = models.IntegerField()
    # ...otros campos según RIPS

class RipsHospitalizacion(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    cod_prestador = models.CharField(max_length=20)
    via_ingreso_servicio = models.CharField(max_length=5)
    fecha_inicio_atencion = models.DateTimeField()
    num_autorizacion = models.CharField(max_length=20)
    causa_motivo_atencion = models.CharField(max_length=5)
    cod_diagnostico_principal = models.CharField(max_length=10)
    cod_diagnostico_principal_e = models.CharField(max_length=10, blank=True, null=True)
    condicion_destino_egreso = models.CharField(max_length=5)
    fecha_egreso = models.DateTimeField()
    consecutivo = models.IntegerField()
    # ...otros campos según RIPS

class RipsOtroServicio(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    cod_prestador = models.CharField(max_length=20)
    num_autorizacion = models.CharField(max_length=20)
    id_mipres = models.CharField(max_length=20, blank=True, null=True)
    fecha_suministro = models.DateTimeField()
    tipo_os = models.CharField(max_length=5)
    cod_tecnologia_salud = models.CharField(max_length=20)
    nom_tecnologia_salud = models.CharField(max_length=255, blank=True, null=True)
    cantidad_os = models.IntegerField()
    vr_unit_os = models.DecimalField(max_digits=12, decimal_places=2)
    vr_servicio = models.DecimalField(max_digits=12, decimal_places=2)
    concepto_recaudo = models.CharField(max_length=5)
    valor_pago_moderador = models.DecimalField(max_digits=12, decimal_places=2)
    consecutivo = models.IntegerField()
    # ...otros campos según RIPS

# Nuevo Modelo para Tarifas Específicas del Contrato
class TarifaContrato(models.Model):
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name='tarifas')
    tipo_item = models.CharField(max_length=20, choices=[('CUPS', 'CUPS'), ('CUMS', 'CUMS'), ('SOAT', 'SOAT'), ('MANUAL', 'Manual')])
    codigo_item = models.CharField(max_length=50, help_text="Código del CUPS, CUMS o servicio específico")
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    valor_acordado = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_vigencia_inicio = models.DateField(blank=True, null=True)
    fecha_vigencia_fin = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ('contrato', 'tipo_item', 'codigo_item') # Para evitar tarifas duplicadas
        verbose_name = "Tarifa de Contrato"
        verbose_name_plural = "Tarifas de Contrato"

    def __str__(self):
        return f"{self.contrato.numero} - {self.tipo_item}: {self.codigo_item} - ${self.valor_acordado}"
