from django.core.management.base import BaseCommand
from django.utils import timezone
from auditoria.models import Glosa, HistorialGlosa


class Command(BaseCommand):
    help = 'Migra el historial de las glosas existentes al nuevo modelo HistorialGlosa'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar sin hacer cambios reales en la base de datos',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Ejecutando en modo DRY-RUN (sin cambios reales)'))
        
        glosas = Glosa.objects.all()
        total_glosas = glosas.count()
        historiales_creados = 0
        
        self.stdout.write(f'Procesando {total_glosas} glosas...')
        
        for glosa in glosas:
            # Crear registro de creación de la glosa
            if not dry_run:
                HistorialGlosa.objects.create(
                    glosa=glosa,
                    accion='creada',
                    descripcion_cambio=f"Glosa creada automáticamente durante migración",
                    fecha_cambio=glosa.fecha_glosa
                )
            historiales_creados += 1
            
            # Si la glosa tiene respuesta de IPS, crear registro
            if glosa.fecha_respuesta:
                if not dry_run:
                    HistorialGlosa.objects.create(
                        glosa=glosa,
                        accion='respondida_ips',
                        estado_anterior='Pendiente',
                        estado_nuevo='Respondida IPS',
                        descripcion_cambio=f"Glosa respondida por IPS. Decisión: {'Aceptada' if glosa.aceptada else 'Rechazada' if glosa.aceptada == False else 'No definida'}",
                        fecha_cambio=glosa.fecha_respuesta
                    )
                historiales_creados += 1
            
            # Si la glosa tiene decisión de ET, crear registro
            if glosa.fecha_decision_et:
                if not dry_run:
                    HistorialGlosa.objects.create(
                        glosa=glosa,
                        accion='decidida_et',
                        estado_anterior='Respondida IPS',
                        estado_nuevo=glosa.estado,
                        valor_anterior=glosa.valor_glosado,
                        valor_nuevo=glosa.valor_aceptado_et,
                        descripcion_cambio=f"Decisión de ET: {glosa.get_estado_display()}. Justificación: {glosa.decision_et_justificacion or 'No especificada'}",
                        fecha_cambio=glosa.fecha_decision_et
                    )
                historiales_creados += 1
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'DRY-RUN completado. Se habrían creado {historiales_creados} registros de historial para {total_glosas} glosas.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Migración completada. Se crearon {historiales_creados} registros de historial para {total_glosas} glosas.'
                )
            ) 