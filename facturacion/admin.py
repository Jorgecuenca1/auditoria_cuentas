from django.contrib import admin
from .models import Factura, Contrato, Paciente, RipsConsulta, RipsMedicamento, RipsProcedimiento, RipsHospitalizacion, RipsOtroServicio, TarifaContrato, Lote, Resolucion, ManualTarifario, Devolucion, CodigoDevolucion, SubcodigoDevolucion, UsuariosNoAptos
from import_export import resources
from import_export.admin import ImportExportModelAdmin


# Recursos para import-export
class FacturaResource(resources.ModelResource):
    class Meta:
        model = Factura
        import_id_fields = ('codigo_uuid',)
        export_order = ('codigo_uuid', 'numero', 'cufe', 'fecha_emision', 'fecha_radicacion', 'ips', 'eps', 'paciente', 'valor_bruto', 'estado', 'tipo_auditoria', 'auditor')


class ContratoResource(resources.ModelResource):
    class Meta:
        model = Contrato
        import_id_fields = ('id',)
        export_order = ('numero', 'vigencia', 'tipo_contrato', 'valor', 'ips', 'objeto', 'fecha_inicio', 'fecha_fin', 'supervisor', 'forma_pago')


class PacienteResource(resources.ModelResource):
    class Meta:
        model = Paciente
        import_id_fields = ('id',)
        export_order = ('tipo_documento', 'numero_documento', 'tipo_usuario', 'fecha_nacimiento', 'sexo', 'pais_residencia', 'municipio_residencia', 'zona_territorial')


class LoteResource(resources.ModelResource):
    class Meta:
        model = Lote
        import_id_fields = ('id',)
        export_order = ('nombre', 'auditor', 'fecha_creacion', 'estado')


class ResolucionResource(resources.ModelResource):
    class Meta:
        model = Resolucion
        import_id_fields = ('numero_resolucion',)
        export_order = ('numero_resolucion', 'entidad_territorial', 'fecha_creacion', 'nombre_firmante')


class TarifaContratoResource(resources.ModelResource):
    class Meta:
        model = TarifaContrato
        import_id_fields = ('id',)
        export_order = ('contrato', 'tipo_item', 'codigo_item', 'descripcion', 'valor_acordado', 'fecha_vigencia_inicio', 'fecha_vigencia_fin')


class ManualTarifarioResource(resources.ModelResource):
    class Meta:
        model = ManualTarifario
        import_id_fields = ('referencia',)
        export_order = ('referencia', 'codigo', 'descripcion', 'uvr')


class CodigoDevolucionResource(resources.ModelResource):
    class Meta:
        model = CodigoDevolucion
        import_id_fields = ('codigo',)
        export_order = ('codigo', 'descripcion')


class SubcodigoDevolucionResource(resources.ModelResource):
    class Meta:
        model = SubcodigoDevolucion
        import_id_fields = ('subcodigo',)
        export_order = ('codigo_padre', 'subcodigo', 'descripcion')


class DevolucionResource(resources.ModelResource):
    class Meta:
        model = Devolucion
        import_id_fields = ('id',)
        export_order = ('factura', 'subcodigo', 'fecha_devolucion', 'justificacion', 'devuelto_por')


class UsuariosNoAptosResource(resources.ModelResource):
    class Meta:
        model = UsuariosNoAptos
        import_id_fields = ('cedula',)
        export_order = ('cedula', 'nombre', 'fecha_registro')


# RIPS Resources
class RipsConsultaResource(resources.ModelResource):
    class Meta:
        model = RipsConsulta
        import_id_fields = ('id',)
        export_order = ('factura', 'paciente', 'cod_prestador', 'fecha_inicio_atencion', 'num_autorizacion', 'cod_consulta', 'vr_servicio')


class RipsMedicamentoResource(resources.ModelResource):
    class Meta:
        model = RipsMedicamento
        import_id_fields = ('id',)
        export_order = ('factura', 'paciente', 'cod_prestador', 'num_autorizacion', 'fecha_dispensacion', 'cod_tecnologia_salud', 'vr_unit_medicamento')


class RipsProcedimientoResource(resources.ModelResource):
    class Meta:
        model = RipsProcedimiento
        import_id_fields = ('id',)
        export_order = ('factura', 'paciente', 'cod_prestador', 'fecha_inicio_atencion', 'num_autorizacion', 'cod_procedimiento', 'vr_servicio')


class RipsHospitalizacionResource(resources.ModelResource):
    class Meta:
        model = RipsHospitalizacion
        import_id_fields = ('id',)
        export_order = ('factura', 'paciente', 'cod_prestador', 'fecha_inicio_atencion', 'fecha_egreso', 'consecutivo')


class RipsOtroServicioResource(resources.ModelResource):
    class Meta:
        model = RipsOtroServicio
        import_id_fields = ('id',)
        export_order = ('factura', 'paciente', 'cod_prestador', 'num_autorizacion', 'fecha_suministro', 'cod_tecnologia_salud', 'vr_servicio')


# Admin classes con import-export
@admin.register(Factura)
class FacturaAdmin(ImportExportModelAdmin):
    resource_class = FacturaResource
    list_display = ('numero', 'cufe', 'ips', 'eps', 'valor_bruto', 'estado', 'fecha_radicacion')
    list_filter = ('estado', 'tipo_auditoria', 'fecha_radicacion', 'ips', 'eps')
    search_fields = ('numero', 'cufe', 'ips__entidad_nombre', 'eps__entidad_nombre')
    readonly_fields = ('codigo_uuid', 'fecha_radicacion')
    ordering = ('-fecha_radicacion',)


@admin.register(Contrato)
class ContratoAdmin(ImportExportModelAdmin):
    resource_class = ContratoResource
    list_display = ('numero', 'tipo_contrato', 'ips', 'valor', 'vigencia', 'fecha_inicio', 'fecha_fin')
    list_filter = ('tipo_contrato', 'vigencia', 'ips')
    search_fields = ('numero', 'ips__entidad_nombre', 'supervisor')
    ordering = ('-vigencia', 'numero')


@admin.register(Paciente)
class PacienteAdmin(ImportExportModelAdmin):
    resource_class = PacienteResource
    list_display = ('tipo_documento', 'numero_documento', 'tipo_usuario', 'fecha_nacimiento', 'sexo')
    list_filter = ('tipo_usuario', 'sexo', 'zona_territorial')
    search_fields = ('numero_documento', 'tipo_documento')
    ordering = ('tipo_documento', 'numero_documento')


@admin.register(Lote)
class LoteAdmin(ImportExportModelAdmin):
    resource_class = LoteResource
    list_display = ('nombre', 'auditor', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion', 'auditor')
    search_fields = ('nombre', 'auditor__username')
    readonly_fields = ('fecha_creacion',)
    ordering = ('-fecha_creacion',)


@admin.register(Resolucion)
class ResolucionAdmin(ImportExportModelAdmin):
    resource_class = ResolucionResource
    list_display = ('numero_resolucion', 'entidad_territorial', 'fecha_creacion', 'nombre_firmante')
    list_filter = ('fecha_creacion', 'entidad_territorial')
    search_fields = ('numero_resolucion', 'entidad_territorial', 'nombre_firmante')
    readonly_fields = ('fecha_creacion',)
    ordering = ('-fecha_creacion',)


@admin.register(TarifaContrato)
class TarifaContratoAdmin(ImportExportModelAdmin):
    resource_class = TarifaContratoResource
    list_display = ('contrato', 'tipo_item', 'codigo_item', 'valor_acordado')
    list_filter = ('tipo_item', 'contrato', 'fecha_vigencia_inicio')
    search_fields = ('codigo_item', 'descripcion', 'contrato__numero')
    ordering = ('contrato', 'tipo_item', 'codigo_item')


@admin.register(ManualTarifario)
class ManualTarifarioAdmin(ImportExportModelAdmin):
    resource_class = ManualTarifarioResource
    list_display = ('referencia', 'codigo', 'descripcion', 'uvr')
    list_filter = ('uvr',)
    search_fields = ('referencia', 'codigo', 'descripcion')
    ordering = ('referencia',)


@admin.register(CodigoDevolucion)
class CodigoDevolucionAdmin(ImportExportModelAdmin):
    resource_class = CodigoDevolucionResource
    list_display = ('codigo', 'descripcion')
    search_fields = ('codigo', 'descripcion')
    ordering = ('codigo',)


@admin.register(SubcodigoDevolucion)
class SubcodigoDevolucionAdmin(ImportExportModelAdmin):
    resource_class = SubcodigoDevolucionResource
    list_display = ('subcodigo', 'codigo_padre', 'descripcion')
    list_filter = ('codigo_padre',)
    search_fields = ('subcodigo', 'descripcion', 'codigo_padre__codigo')
    ordering = ('codigo_padre', 'subcodigo')


@admin.register(Devolucion)
class DevolucionAdmin(ImportExportModelAdmin):
    resource_class = DevolucionResource
    list_display = ('factura', 'subcodigo', 'fecha_devolucion', 'devuelto_por')
    list_filter = ('fecha_devolucion', 'subcodigo__codigo_padre', 'devuelto_por')
    search_fields = ('factura__numero', 'justificacion', 'devuelto_por__username')
    readonly_fields = ('fecha_devolucion',)
    ordering = ('-fecha_devolucion',)


@admin.register(UsuariosNoAptos)
class UsuariosNoAptosAdmin(ImportExportModelAdmin):
    resource_class = UsuariosNoAptosResource
    list_display = ('cedula', 'nombre', 'fecha_registro')
    search_fields = ('cedula', 'nombre')
    readonly_fields = ('fecha_registro',)
    ordering = ('-fecha_registro',)


# RIPS Admin classes
@admin.register(RipsConsulta)
class RipsConsultaAdmin(ImportExportModelAdmin):
    resource_class = RipsConsultaResource
    list_display = ('factura', 'paciente', 'cod_consulta', 'vr_servicio', 'fecha_inicio_atencion')
    list_filter = ('fecha_inicio_atencion', 'modalidad_grupo_servicio')
    search_fields = ('factura__numero', 'paciente__numero_documento', 'cod_consulta')
    ordering = ('-fecha_inicio_atencion',)


@admin.register(RipsMedicamento)
class RipsMedicamentoAdmin(ImportExportModelAdmin):
    resource_class = RipsMedicamentoResource
    list_display = ('factura', 'paciente', 'cod_tecnologia_salud', 'vr_unit_medicamento', 'fecha_dispensacion')
    list_filter = ('fecha_dispensacion', 'tipo_medicamento')
    search_fields = ('factura__numero', 'paciente__numero_documento', 'cod_tecnologia_salud')
    ordering = ('-fecha_dispensacion',)


@admin.register(RipsProcedimiento)
class RipsProcedimientoAdmin(ImportExportModelAdmin):
    resource_class = RipsProcedimientoResource
    list_display = ('factura', 'paciente', 'cod_procedimiento', 'vr_servicio', 'fecha_inicio_atencion')
    list_filter = ('fecha_inicio_atencion', 'modalidad_grupo_servicio')
    search_fields = ('factura__numero', 'paciente__numero_documento', 'cod_procedimiento')
    ordering = ('-fecha_inicio_atencion',)


@admin.register(RipsHospitalizacion)
class RipsHospitalizacionAdmin(ImportExportModelAdmin):
    resource_class = RipsHospitalizacionResource
    list_display = ('factura', 'paciente', 'fecha_inicio_atencion', 'fecha_egreso', 'consecutivo')
    list_filter = ('fecha_inicio_atencion', 'fecha_egreso', 'via_ingreso_servicio')
    search_fields = ('factura__numero', 'paciente__numero_documento')
    ordering = ('-fecha_inicio_atencion',)


@admin.register(RipsOtroServicio)
class RipsOtroServicioAdmin(ImportExportModelAdmin):
    resource_class = RipsOtroServicioResource
    list_display = ('factura', 'paciente', 'cod_tecnologia_salud', 'vr_servicio', 'fecha_suministro')
    list_filter = ('fecha_suministro', 'tipo_os')
    search_fields = ('factura__numero', 'paciente__numero_documento', 'cod_tecnologia_salud')
    ordering = ('-fecha_suministro',)