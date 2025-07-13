from django.core.management.base import BaseCommand
from django.db import transaction
from facturacion.models import Factura
from cartera.models import CuentaCartera
from decimal import Decimal

class Command(BaseCommand):
    help = 'Poblar cuentas de cartera para facturas existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar la recreación de cuentas existentes',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        # Obtener facturas que no tienen cuenta de cartera
        facturas_sin_cuenta = Factura.objects.filter(cuentacartera__isnull=True)  # type: ignore
        
        if force:
            facturas_sin_cuenta = Factura.objects.all()  # type: ignore
            self.stdout.write(self.style.WARNING('Modo FORCE: Se recrearán todas las cuentas de cartera'))  # type: ignore
        
        total_facturas = facturas_sin_cuenta.count()
        self.stdout.write(f'Procesando {total_facturas} facturas...')
        
        created_count = 0
        updated_count = 0
        
        with transaction.atomic():
            for factura in facturas_sin_cuenta:
                try:
                    if force:
                        # Eliminar cuenta existente si existe
                        CuentaCartera.objects.filter(factura=factura).delete()  # type: ignore
                    
                    # Crear cuenta de cartera
                    cuenta, created = CuentaCartera.objects.get_or_create(  # type: ignore
                        factura=factura,
                        defaults={
                            'ips': factura.ips,
                            'eps': factura.eps,
                            'valor_inicial': factura.valor_bruto,
                            'valor_glosado_provisional': Decimal('0'),
                            'valor_glosado_definitivo': Decimal('0'),
                            'valor_pagable': factura.valor_bruto,
                            'estado_pago': 'Pendiente'
                        }
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(f'✓ Creada cuenta para factura {factura.numero}')
                    else:
                        updated_count += 1
                        self.stdout.write(f'→ Ya existe cuenta para factura {factura.numero}')
                    
                    # Actualizar valores de glosas
                    cuenta.actualizar_valores_glosas()
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error procesando factura {factura.numero}: {str(e)}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Proceso completado: {created_count} cuentas creadas, {updated_count} cuentas ya existían'
            )
        ) 