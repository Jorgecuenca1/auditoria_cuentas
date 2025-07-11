from django.db import models
from accounts.models import Profile
from django.conf import settings
import uuid

class Lote(models.Model):
    ESTADOS_LOTE = (
        ('Pendiente', 'Pendiente de Asignación'),
        ('Asignado', 'Asignado a Auditor'),
        ('En Auditoria', 'En Auditoría'),
        ('Auditado', 'Auditado'),
        ('Finalizado', 'Finalizado'),
    )
    nombre = models.CharField(max_length=100, unique=True, help_text="Nombre o código único para el lote")
    auditor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='lotes_asignados', help_text="Auditor asignado a este lote de facturas")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_LOTE, default='Pendiente')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Lote de Facturas"
        verbose_name_plural = "Lotes de Facturas"

class Contrato(models.Model):
    numero = models.CharField(max_length=50)
    vigencia = models.IntegerField(blank=True, null=True, help_text="Año de vigencia del contrato")
    TIPO_CONTRATO_CHOICES = [
        ('Contrato', 'Con Contrato'),
        ('Sin Contrato', 'Sin Contrato'),
    ]
    tipo_contrato = models.CharField(max_length=20, choices=TIPO_CONTRATO_CHOICES, blank=True, null=True)
    valor = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    ips = models.ForeignKey(
        'accounts.Profile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contratos_ips',
        limit_choices_to={'role': 'IPS'},
        help_text="IPS asociada a este contrato"
    )
    objeto = models.TextField(blank=True, null=True, help_text="Objeto o descripción del contrato")
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    supervisor = models.CharField(max_length=255, blank=True, null=True, help_text="Nombre del supervisor del contrato")
    FORMA_PAGO_CHOICES = [
        ('10A - 30PP 60 sp', '10A - 30PP 60 sp'),
        # Agrega más opciones si es necesario
    ]
    forma_pago = models.CharField(max_length=50, choices=FORMA_PAGO_CHOICES, blank=True, null=True)
    fecha_liquidacion = models.DateField(blank=True, null=True)
    fecha_conciliacion = models.DateField(blank=True, null=True)
    fecha_presupuesto = models.DateField(blank=True, null=True)
    servicios_cubiertos = models.TextField(blank=True, null=True)
    tarifario_adjunto = models.FileField(upload_to='tarifarios/', blank=True, null=True, help_text="Adjunto del tarifario general asociado a este contrato")
    condiciones_pago = models.TextField(blank=True, null=True)
    adjunto = models.FileField(upload_to='contratos/', blank=True, null=True, help_text="Adjunto del contrato completo")
    alerta_vencimiento = models.BooleanField(default=False)
    def __str__(self):
        return f"Contrato {self.numero} ({self.tipo_contrato})"

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
    ESTADO_CHOICES = [
        ('Radicada', 'Radicada'),
        ('Devuelta', 'Devuelta'),
        ('En Auditoria', 'En Auditoría'),
        ('Auditada', 'Auditada'),
    ]
    TIPO_AUDITORIA_CHOICES = [
        ('Acuerdo', 'Acuerdo'),
        ('Contrato', 'Contrato'),
        ('Ambulatorio', 'Ambulatorio'),
        ('Hospitalizacion', 'Hospitalización'),
        ('Urgencias', 'Urgencias'),
    ]
    codigo_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, help_text="Código único automático de la factura")
    numero = models.CharField(max_length=50)
    cufe = models.CharField(max_length=150)
    fecha_emision = models.DateField()
    fecha_radicacion = models.DateField(auto_now_add=True)
    ips = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='facturas_ips')
    eps = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='facturas_eps')
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, null=True, blank=True)
    valor_bruto = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="Radicada")
    archivo_rips = models.FileField(upload_to='rips/')
    archivo_pdf = models.FileField(upload_to='facturas_pdf/', blank=True, null=True, help_text="Archivo PDF de la factura")
    contrato = models.ForeignKey('Contrato', on_delete=models.SET_NULL, null=True, blank=True)
    lote = models.ForeignKey(Lote, on_delete=models.SET_NULL, null=True, blank=True, related_name='facturas', help_text="Lote al que pertenece esta factura")
    auditor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='facturas_auditadas', limit_choices_to={'profile__role': 'AUDITOR'})
    tipo_auditoria = models.CharField(max_length=20, choices=TIPO_AUDITORIA_CHOICES, null=True, blank=True, help_text="Tipo de auditoría para la factura")
    def __str__(self):
        return f"Factura {self.numero} (UUID: {self.codigo_uuid}) CUFE {self.cufe}"

class UsuariosNoAptos(models.Model):
    cedula = models.CharField(max_length=20, unique=True, help_text="Número de cédula del usuario no apto")
    nombre = models.CharField(max_length=255, help_text="Nombre completo del usuario no apto")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.cedula})"

    class Meta:
        verbose_name = "Usuario No Apto"
        verbose_name_plural = "Usuarios No Aptos"

class CodigoDevolucion(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.codigo} - {self.descripcion[:50]}"

    class Meta:
        verbose_name = "Código de Devolución"
        verbose_name_plural = "Códigos de Devolución"

class SubcodigoDevolucion(models.Model):
    codigo_padre = models.ForeignKey(CodigoDevolucion, on_delete=models.CASCADE, related_name='subcodigos')
    subcodigo = models.CharField(max_length=10, unique=True)
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.subcodigo} - {self.descripcion[:50]}"

    class Meta:
        verbose_name = "Subcódigo de Devolución"
        verbose_name_plural = "Subcódigos de Devolución"

class Devolucion(models.Model):
    factura = models.OneToOneField(Factura, on_delete=models.CASCADE, related_name='devolucion')
    subcodigo = models.ForeignKey(SubcodigoDevolucion, on_delete=models.PROTECT)
    fecha_devolucion = models.DateTimeField(auto_now_add=True)
    justificacion = models.TextField(blank=True, null=True, help_text="Justificación adicional para la devolución.")
    devuelto_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, help_text="Usuario que registró la devolución (para devoluciones manuales)")

    def __str__(self):
        return f"Devolución de Factura {self.factura.numero} - Motivo: {self.subcodigo.subcodigo}"

    class Meta:
        verbose_name = "Devolución"
        verbose_name_plural = "Devoluciones"

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

class Resolucion(models.Model):
    numero_resolucion = models.CharField(max_length=50, unique=True, help_text="Número único de la resolución")
    entidad_territorial = models.CharField(max_length=255, help_text="Nombre de la Secretaría de Salud que emite la resolución")
    fecha_creacion = models.DateField(auto_now_add=True)
    nombre_firmante = models.CharField(max_length=255, help_text="Nombre completo del firmante de la resolución")
    facturas = models.ManyToManyField(Factura, related_name='resoluciones', blank=True, help_text="Facturas aprobadas por esta resolución")
    cuerpo_resolucion_html = models.TextField(blank=True, null=True, help_text="Contenido HTML generado de la resolución")
    archivo_pdf = models.FileField(upload_to='resoluciones_pdf/', blank=True, null=True, help_text="Archivo PDF de la resolución")

    def __str__(self):
        return f"Resolución N.º {self.numero_resolucion} de {self.entidad_territorial}"

    class Meta:
        verbose_name = "Resolución"
        verbose_name_plural = "Resoluciones"

class ManualTarifario(models.Model):
    referencia = models.CharField(max_length=50, unique=True, help_text="Referencia única del item tarifario")
    codigo = models.CharField(max_length=50, unique=True, help_text="Código del CUPS, CUMS o servicio específico")
    descripcion = models.TextField(help_text="Descripción detallada del item")
    uvr = models.DecimalField(max_digits=12, decimal_places=2, help_text="Unidad de Valor Relativa (UVR)")

    def __str__(self):
        return f"{self.codigo} - {self.descripcion} ({self.uvr} UVR)"

    class Meta:
        verbose_name = "Manual Tarifario"
        verbose_name_plural = "Manuales Tarifarios"
