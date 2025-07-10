# Sistema de Historial de Glosas

## Descripción

Se ha implementado un sistema completo de historial para las glosas que registra automáticamente todos los cambios y acciones importantes que ocurren durante el ciclo de vida de una glosa.

## Características Principales

### 1. Modelo HistorialGlosa

El nuevo modelo `HistorialGlosa` registra:
- **Usuario que realizó la acción**: Quién hizo el cambio
- **Tipo de acción**: Creación, respuesta IPS, decisión ET, devolución, etc.
- **Cambios de estado**: Estado anterior y nuevo
- **Cambios de valores**: Valores anteriores y nuevos
- **Descripción detallada**: Explicación del cambio
- **Información técnica**: IP del usuario, User Agent, timestamp

### 2. Acciones Registradas Automáticamente

- **Glosa Creada**: Cuando se crea una nueva glosa
- **Respondida por IPS**: Cuando la IPS responde a una glosa
- **Decidida por ET**: Cuando la ET toma una decisión sobre la respuesta de la IPS
- **Devuelta a IPS**: Cuando la ET devuelve la glosa para reevaluación
- **Archivo Adjuntado**: Cuando se adjunta un archivo de soporte
- **Valor Modificado**: Cuando se cambia el valor de la glosa
- **Justificación Agregada**: Cuando se agrega una justificación

### 3. Vista de Historial

- **URL**: `/auditoria/glosa/<id>/historial/`
- **Permisos**: IPS, ET, AUDITOR (con restricciones por rol)
- **Características**:
  - Timeline visual de todos los cambios
  - Información detallada de cada acción
  - Filtros por tipo de acción
  - Información del usuario y IP

### 4. Integración en la Interfaz

- **Enlace en glosas pendientes**: Botón de historial en cada fila
- **Enlace en auditar factura**: Botón de historial en la tabla de glosas
- **Iconos intuitivos**: Diferentes iconos para cada tipo de acción

## Beneficios

### Para la Auditoría
- **Trazabilidad completa**: Se puede rastrear cada cambio en una glosa
- **Auditoría forense**: Información de IP y User Agent para investigaciones
- **Compliance**: Cumplimiento con regulaciones que requieren auditoría de cambios

### Para la Gestión
- **Transparencia**: Todos los usuarios pueden ver el historial completo
- **Responsabilidad**: Se registra quién hizo cada cambio
- **Análisis**: Datos para mejorar procesos y identificar patrones

### Para las IPS
- **Seguimiento**: Pueden ver el estado de sus glosas en tiempo real
- **Historial**: Acceso completo al historial de sus propias glosas
- **Justificación**: Entienden por qué se tomaron ciertas decisiones

## Implementación Técnica

### Modelo de Datos
```python
class HistorialGlosa(models.Model):
    glosa = models.ForeignKey(Glosa, on_delete=models.CASCADE, related_name='historial')
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    accion = models.CharField(max_length=50, choices=ACCION_CHOICES)
    estado_anterior = models.CharField(max_length=20, blank=True, null=True)
    estado_nuevo = models.CharField(max_length=20, blank=True, null=True)
    valor_anterior = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    valor_nuevo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    descripcion_cambio = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
```

### Método de Registro
```python
@classmethod
def registrar_cambio(cls, glosa, accion, usuario=None, estado_anterior=None, 
                    estado_nuevo=None, valor_anterior=None, valor_nuevo=None, 
                    descripcion_cambio=None, request=None):
    # Registra automáticamente un cambio en el historial
```

### Integración en Vistas
- **Crear glosa**: Registra la creación automáticamente
- **Responder glosa**: Registra la respuesta de la IPS
- **Decidir glosa**: Registra la decisión de la ET
- **Devolver glosa**: Registra la devolución a la IPS

## Migración de Datos Existentes

Se ha creado un comando de gestión para migrar el historial de las glosas existentes:

```bash
# Ejecutar en modo dry-run (sin cambios)
python manage.py migrar_historial_glosas --dry-run

# Ejecutar la migración real
python manage.py migrar_historial_glosas
```

## Uso

### Para Ver el Historial de una Glosa

1. **Desde glosas pendientes**: Hacer clic en el icono de historial (reloj)
2. **Desde auditar factura**: Hacer clic en el botón "Historial"
3. **URL directa**: `/auditoria/glosa/<id>/historial/`

### Para Administradores

El historial está disponible en el admin de Django en:
- **Modelo**: `HistorialGlosa`
- **Filtros**: Por acción, fecha, usuario
- **Búsqueda**: Por glosa, factura, usuario
- **Solo lectura**: No se pueden modificar registros del historial

## Consideraciones de Seguridad

- **Permisos por rol**: IPS solo puede ver historial de sus propias glosas
- **Información sensible**: IP y User Agent se registran para auditoría
- **Solo lectura**: Los registros del historial no se pueden modificar
- **Logging**: Todos los cambios se registran automáticamente

## Próximas Mejoras

1. **Exportación**: Funcionalidad para exportar historial a PDF/Excel
2. **Notificaciones**: Alertas cuando se realizan cambios importantes
3. **Análisis**: Dashboard con estadísticas del historial
4. **API**: Endpoints para consultar historial programáticamente
5. **Filtros avanzados**: Búsqueda por fechas, usuarios, acciones específicas 