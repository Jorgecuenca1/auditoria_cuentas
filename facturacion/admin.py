from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import (
    Factura, Paciente, Contrato, RipsConsulta, RipsMedicamento,
    RipsProcedimiento, RipsHospitalizacion, RipsOtroServicio, ManualTarifario,
    UsuariosNoAptos, CodigoDevolucion, SubcodigoDevolucion, Devolucion, Lote, Resolucion
)

# Resources para import/export
class UsuariosNoAptosResource(resources.ModelResource):
    class Meta:
        model = UsuariosNoAptos
        import_id_fields = ('cedula',)
        fields = ('id', 'cedula', 'nombre', 'fecha_registro')

class CodigoDevolucionResource(resources.ModelResource):
    class Meta:
        model = CodigoDevolucion
        import_id_fields = ('codigo',)
        fields = ('id', 'codigo', 'descripcion')

class SubcodigoDevolucionResource(resources.ModelResource):
    class Meta:
        model = SubcodigoDevolucion
        import_id_fields = ('subcodigo',)
        fields = ('id', 'subcodigo', 'descripcion', 'codigo_padre')

class FacturaResource(resources.ModelResource):
    class Meta:
        model = Factura
        import_id_fields = ('numero',)
        fields = ('id', 'codigo_uuid', 'numero', 'cufe', 'fecha_emision', 'fecha_radicacion', 'ips', 'eps', 'paciente', 'valor_bruto', 'estado', 'contrato', 'lote', 'auditor', 'tipo_auditoria')

class PacienteResource(resources.ModelResource):
    class Meta:
        model = Paciente
        import_id_fields = ('numero_documento',)
        fields = ('id', 'numero_documento', 'tipo_documento', 'tipo_usuario', 'fecha_nacimiento', 'sexo', 'pais_residencia', 'municipio_residencia', 'zona_territorial', 'incapacidad', 'pais_origen')

class ContratoResource(resources.ModelResource):
    class Meta:
        model = Contrato
        import_id_fields = ('numero',)
        fields = ('id', 'numero', 'vigencia', 'tipo_contrato', 'valor', 'ips', 'objeto', 'fecha_inicio', 'fecha_fin', 'supervisor', 'forma_pago', 'alerta_vencimiento')

class RipsConsultaResource(resources.ModelResource):
    class Meta:
        model = RipsConsulta
        import_id_fields = ('id',)
        fields = ('id', 'factura', 'paciente', 'cod_prestador', 'fecha_inicio_atencion', 'num_autorizacion', 'cod_consulta', 'modalidad_grupo_servicio', 'grupo_servicios', 'cod_servicio', 'finalidad_tecnologia', 'causa_motivo_atencion', 'cod_diagnostico_principal', 'tipo_diagnostico_principal', 'vr_servicio', 'concepto_recaudo', 'valor_pago_moderador', 'consecutivo')

class RipsMedicamentoResource(resources.ModelResource):
    class Meta:
        model = RipsMedicamento
        import_id_fields = ('id',)
        fields = ('id', 'factura', 'paciente', 'cod_prestador', 'num_autorizacion', 'id_mipres', 'fecha_dispensacion', 'cod_diagnostico_principal', 'tipo_medicamento', 'cod_tecnologia_salud', 'nom_tecnologia_salud', 'concentracion_medicamento', 'unidad_medida', 'forma_farmaceutica', 'unidad_min_dispensa', 'cantidad_medicamento', 'dias_tratamiento', 'vr_unit_medicamento', 'vr_servicio', 'concepto_recaudo', 'valor_pago_moderador', 'consecutivo')

class RipsProcedimientoResource(resources.ModelResource):
    class Meta:
        model = RipsProcedimiento
        import_id_fields = ('id',)
        fields = ('id', 'factura', 'paciente', 'cod_prestador', 'fecha_inicio_atencion', 'num_autorizacion', 'cod_procedimiento', 'via_ingreso_servicio', 'modalidad_grupo_servicio', 'grupo_servicios', 'cod_servicio', 'finalidad_tecnologia', 'cod_diagnostico_principal', 'vr_servicio', 'concepto_recaudo', 'valor_pago_moderador', 'consecutivo')

class RipsHospitalizacionResource(resources.ModelResource):
    class Meta:
        model = RipsHospitalizacion
        import_id_fields = ('id',)
        fields = ('id', 'factura', 'paciente', 'cod_prestador', 'via_ingreso_servicio', 'fecha_inicio_atencion', 'num_autorizacion', 'causa_motivo_atencion', 'cod_diagnostico_principal', 'cod_diagnostico_principal_e', 'condicion_destino_egreso', 'fecha_egreso', 'consecutivo')

class RipsOtroServicioResource(resources.ModelResource):
    class Meta:
        model = RipsOtroServicio
        import_id_fields = ('id',)
        fields = ('id', 'factura', 'paciente', 'cod_prestador', 'num_autorizacion', 'id_mipres', 'fecha_suministro', 'tipo_os', 'cod_tecnologia_salud', 'nom_tecnologia_salud', 'cantidad_os', 'vr_unit_os', 'vr_servicio', 'concepto_recaudo', 'valor_pago_moderador', 'consecutivo')

class ManualTarifarioResource(resources.ModelResource):
    class Meta:
        model = ManualTarifario
        import_id_fields = ('codigo',)
        fields = ('id', 'referencia', 'codigo', 'descripcion', 'uvr')

class DevolucionResource(resources.ModelResource):
    class Meta:
        model = Devolucion
        import_id_fields = ('id',)
        fields = ('id', 'factura', 'subcodigo', 'fecha_devolucion', 'justificacion', 'devuelto_por')

class LoteResource(resources.ModelResource):
    class Meta:
        model = Lote
        import_id_fields = ('id',)
        fields = ('id', 'nombre', 'auditor', 'fecha_creacion', 'estado')

class ResolucionResource(resources.ModelResource):
    class Meta:
        model = Resolucion
        import_id_fields = ('numero_resolucion',)
        fields = ('id', 'numero_resolucion', 'entidad_territorial', 'fecha_creacion', 'nombre_firmante', 'cuerpo_resolucion_html')

# Admin classes con import/export
@admin.register(UsuariosNoAptos)
class UsuariosNoAptosAdmin(ImportExportModelAdmin):
    resource_class = UsuariosNoAptosResource
    list_display = ('cedula', 'nombre', 'fecha_registro')
    search_fields = ('cedula', 'nombre')

@admin.register(CodigoDevolucion)
class CodigoDevolucionAdmin(ImportExportModelAdmin):
    resource_class = CodigoDevolucionResource
    list_display = ('codigo', 'descripcion')

@admin.register(SubcodigoDevolucion)
class SubcodigoDevolucionAdmin(ImportExportModelAdmin):
    resource_class = SubcodigoDevolucionResource
    list_display = ('subcodigo', 'descripcion', 'codigo_padre')
    list_filter = ('codigo_padre',)

@admin.register(Factura)
class FacturaAdmin(ImportExportModelAdmin):
    resource_class = FacturaResource
    list_display = ('codigo_uuid', 'numero', 'ips', 'eps', 'valor_bruto', 'estado', 'fecha_radicacion')
    list_filter = ('estado', 'fecha_radicacion', 'ips', 'eps')
    search_fields = ('numero', 'cufe', 'codigo_uuid', 'ips__entidad_nombre', 'eps__entidad_nombre')
    readonly_fields = ('codigo_uuid',)

@admin.register(Paciente)
class PacienteAdmin(ImportExportModelAdmin):
    resource_class = PacienteResource
    list_display = ('numero_documento', 'tipo_documento', 'fecha_nacimiento', 'sexo')
    list_filter = ('tipo_documento', 'sexo', 'fecha_nacimiento')
    search_fields = ('numero_documento', 'tipo_documento')

@admin.register(Contrato)
class ContratoAdmin(ImportExportModelAdmin):
    resource_class = ContratoResource
    list_display = ('numero', 'tipo_contrato', 'fecha_inicio', 'fecha_fin', 'ips', 'valor', 'alerta_vencimiento')
    list_filter = ('tipo_contrato', 'alerta_vencimiento', 'fecha_inicio', 'fecha_fin')
    search_fields = ('numero', 'ips__entidad_nombre')

@admin.register(RipsConsulta)
class RipsConsultaAdmin(ImportExportModelAdmin):
    resource_class = RipsConsultaResource
    list_display = ('factura', 'fecha_inicio_atencion', 'cod_consulta', 'vr_servicio')
    list_filter = ('fecha_inicio_atencion', 'finalidad_tecnologia', 'causa_motivo_atencion')
    search_fields = ('factura__numero', 'cod_consulta', 'cod_diagnostico_principal')

@admin.register(RipsMedicamento)
class RipsMedicamentoAdmin(ImportExportModelAdmin):
    resource_class = RipsMedicamentoResource
    list_display = ('factura', 'cod_tecnologia_salud', 'nom_tecnologia_salud', 'cantidad_medicamento', 'vr_servicio')
    list_filter = ('tipo_medicamento', 'forma_farmaceutica')
    search_fields = ('factura__numero', 'cod_tecnologia_salud', 'nom_tecnologia_salud')

@admin.register(RipsProcedimiento)
class RipsProcedimientoAdmin(ImportExportModelAdmin):
    resource_class = RipsProcedimientoResource
    list_display = ('factura', 'fecha_inicio_atencion', 'cod_procedimiento', 'vr_servicio')
    list_filter = ('via_ingreso_servicio', 'finalidad_tecnologia')
    search_fields = ('factura__numero', 'cod_procedimiento', 'cod_diagnostico_principal')

@admin.register(RipsHospitalizacion)
class RipsHospitalizacionAdmin(ImportExportModelAdmin):
    resource_class = RipsHospitalizacionResource
    list_display = ('factura', 'fecha_inicio_atencion', 'fecha_egreso')
    list_filter = ('causa_motivo_atencion',)
    search_fields = ('factura__numero', 'cod_diagnostico_principal')

@admin.register(RipsOtroServicio)
class RipsOtroServicioAdmin(ImportExportModelAdmin):
    resource_class = RipsOtroServicioResource
    list_display = ('factura', 'fecha_suministro', 'cod_tecnologia_salud', 'nom_tecnologia_salud', 'vr_servicio')
    search_fields = ('factura__numero', 'cod_tecnologia_salud', 'nom_tecnologia_salud')

@admin.register(ManualTarifario)
class ManualTarifarioAdmin(ImportExportModelAdmin):
    resource_class = ManualTarifarioResource
    list_display = ('codigo', 'descripcion', 'uvr')
    search_fields = ('codigo', 'descripcion')

@admin.register(Devolucion)
class DevolucionAdmin(ImportExportModelAdmin):
    resource_class = DevolucionResource
    list_display = ('factura', 'fecha_devolucion', 'subcodigo', 'devuelto_por')
    list_filter = ('fecha_devolucion',)
    search_fields = ('factura__numero', 'subcodigo__descripcion')

@admin.register(Lote)
class LoteAdmin(ImportExportModelAdmin):
    resource_class = LoteResource
    list_display = ('nombre', 'fecha_creacion', 'auditor', 'estado')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('nombre', 'auditor__username')

@admin.register(Resolucion)
class ResolucionAdmin(ImportExportModelAdmin):
    resource_class = ResolucionResource
    list_display = ('numero_resolucion', 'entidad_territorial', 'fecha_creacion', 'nombre_firmante')
    list_filter = ('fecha_creacion',)
    search_fields = ('numero_resolucion', 'entidad_territorial', 'nombre_firmante')