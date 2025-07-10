# Historial de Glosas en Reporte de Auditoría Detalle

## Descripción

Se ha integrado el sistema de historial de glosas en el reporte de auditoría detalle, permitiendo visualizar el historial completo de cada glosa directamente desde la tabla de seguimiento.

## Características Implementadas

### 1. Columna de Historial en la Tabla

- **Nueva columna**: Se agregó una columna "Historial" a la tabla de seguimiento de glosas
- **Dropdown interactivo**: Cada glosa muestra un botón con el número de registros de historial
- **Vista previa**: Al hacer clic se muestra un dropdown con los últimos 8 registros del historial
- **Enlace completo**: Botón para ver el historial completo de cada glosa

### 2. Información Mostrada en el Dropdown

- **Fecha y hora**: Timestamp de cada cambio
- **Tipo de acción**: Badge con el tipo de acción realizada
- **Usuario**: Quién realizó la acción
- **Cambios de estado**: Estados anterior y nuevo (si aplica)
- **Descripción**: Explicación del cambio (truncada a 80 caracteres)
- **Contador**: Muestra cuántos registros más hay disponibles

### 3. Resumen de Estadísticas

Se agregó una tercera columna en el resumen que muestra:
- **Total Registros Historial**: Número total de registros de historial para todas las glosas
- **Glosas con Historial**: Cuántas glosas tienen al menos un registro de historial
- **Última Actividad**: Fecha de la última actividad registrada

## Estructura de la Tabla Actualizada

```
| Fecha Glosa | Tipo Glosa | Descripción | Valor | Estado | Respuesta IPS | Decisión ET | Historial |
|-------------|------------|-------------|-------|--------|---------------|-------------|-----------|
| 2025-07-09  | 1 - Tipo   | Descripción | $22   | Aceptada| ...          | ...         | [3] ▼     |
```

### Dropdown de Historial

```
┌─ Historial de Glosa #123 ──────────────────────┐
│ 09/07/2025 14:30  [Glosa Creada]              │
│ 👤 Juan Pérez                                  │
│ Glosa creada por Juan Pérez                    │
├─────────────────────────────────────────────────┤
│ 10/07/2025 09:15  [Respondida por IPS]        │
│ 👤 María López                                  │
│ Pendiente → Respondida IPS                     │
│ Glosa respondida por IPS. Decisión: Aceptada   │
├─────────────────────────────────────────────────┤
│ 10/07/2025 16:45  [Decidida por ET]           │
│ 👤 Carlos Ruiz                                  │
│ Respondida IPS → Aceptada ET                   │
│ Respuesta de la IPS aceptada. Glosa levantada  │
├─────────────────────────────────────────────────┤
│ [Ver Historial Completo]                       │
└─────────────────────────────────────────────────┘
```

## Beneficios

### Para Auditores y ET
- **Vista rápida**: Pueden ver el historial sin salir del reporte
- **Contexto completo**: Entienden el flujo completo de cada glosa
- **Trazabilidad**: Rastrean quién hizo qué y cuándo
- **Eficiencia**: No necesitan navegar a otra página para ver detalles

### Para Gestión
- **Reportes completos**: El reporte incluye toda la información necesaria
- **Auditoría forense**: Información de IP y usuarios para investigaciones
- **Análisis de procesos**: Pueden identificar patrones y cuellos de botella

### Para Compliance
- **Documentación completa**: Todo el historial está documentado
- **Auditoría regulatoria**: Cumple con requisitos de auditoría
- **Responsabilidad**: Se registra quién hizo cada cambio

## Implementación Técnica

### Modificaciones en la Vista

```python
# En reporte_auditoria_detalle
glosas = Glosa.objects.filter(factura=factura).select_related(
    'tipo_glosa', 'subtipo_glosa', 'subcodigo_glosa',
    'tipo_glosa_respuesta', 'subtipo_glosa_respuesta'
).prefetch_related(
    'historial', 'historial__usuario'  # Nuevo: incluir historial
).order_by('fecha_glosa')

# Calcular estadísticas del historial
total_historial = sum(glosa.historial.count() for glosa in glosas)
glosas_con_historial = sum(1 for glosa in glosas if glosa.historial.count() > 0)
```

### Modificaciones en la Plantilla

```html
<!-- Nueva columna en el header -->
<th rowspan="2">Historial</th>

<!-- Nueva celda en cada fila -->
<td>
    {% if glosa.historial.all %}
        <div class="dropdown">
            <button class="btn btn-outline-info btn-sm dropdown-toggle">
                <i class="bi bi-clock-history"></i> {{ glosa.historial.count }}
            </button>
            <ul class="dropdown-menu">
                <!-- Contenido del historial -->
            </ul>
        </div>
    {% else %}
        <span class="text-muted">Sin historial</span>
    {% endif %}
</td>
```

## Uso

### Para Ver el Historial de una Glosa

1. **Desde el reporte**: Hacer clic en el botón de historial en la columna correspondiente
2. **Vista previa**: Ver los últimos 8 registros en el dropdown
3. **Vista completa**: Hacer clic en "Ver Historial Completo" para ir a la página dedicada

### Navegación

- **Dropdown**: Muestra vista previa rápida
- **Enlace completo**: Lleva a la página de historial detallado
- **Responsive**: Funciona en dispositivos móviles

## Consideraciones de Rendimiento

- **Prefetch relacionado**: Se optimiza la consulta para evitar N+1 queries
- **Límite de registros**: Solo se muestran los últimos 8 en el dropdown
- **Carga diferida**: El historial completo se carga solo cuando se solicita

## Próximas Mejoras

1. **Filtros en dropdown**: Permitir filtrar por tipo de acción
2. **Exportación**: Incluir historial en reportes PDF/Excel
3. **Notificaciones**: Alertas para cambios importantes
4. **Timeline visual**: Mostrar el historial como una línea de tiempo
5. **Búsqueda**: Buscar en el historial por texto o fecha 