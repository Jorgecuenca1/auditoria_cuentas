from django import forms
from .models import Factura, Contrato, Paciente, RipsConsulta, RipsMedicamento, RipsProcedimiento, RipsHospitalizacion, RipsOtroServicio, TarifaContrato, Lote, Resolucion, ManualTarifario
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from accounts.models import Profile # Importar el modelo Profile

User = get_user_model()

class LoteForm(forms.ModelForm):
    facturas = forms.ModelMultipleChoiceField(
        queryset=Factura.objects.filter(lote__isnull=True, estado_auditoria='Radicada', auditor__isnull=True).order_by('ips__entidad_nombre'),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Facturas para incluir en el lote (solo se muestran facturas 'Radicadas' sin lote y sin auditor asignado)"
    )

    class Meta:
        model = Lote
        fields = ['nombre', 'facturas']
        help_texts = {
            'nombre': 'Asigna un nombre descriptivo al lote para identificarlo fácilmente.',
        }

    def clean_facturas(self):
        facturas = self.cleaned_data.get('facturas')
        if not facturas:
            raise ValidationError("Debes seleccionar al menos una factura para el lote.")

        # Verificar que todas las facturas pertenecen a la misma IPS
        primer_factura_ips = None
        for factura in facturas:
            if primer_factura_ips is None:
                primer_factura_ips = factura.ips
            elif factura.ips != primer_factura_ips:
                raise ValidationError("Todas las facturas seleccionadas deben pertenecer a la misma IPS.")
        return facturas


class AsignarAuditorLoteForm(forms.ModelForm):
    auditor = forms.ModelChoiceField(
        queryset=None, # Se definirá en __init__
        required=True,
        label="Seleccionar Auditor para el Lote"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['auditor'].queryset = User.objects.filter(profile__role='AUDITOR')

    class Meta:
        model = Lote
        fields = ['auditor']

class FacturaForm(forms.ModelForm):
    fecha_emision = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Factura
        fields = ['numero', 'cufe', 'fecha_emision', 'eps', 'valor_bruto', 'archivo_rips']

class RipsUploadForm(forms.Form):
    rips_file = forms.FileField(label="Archivo RIPS (JSON)")

class ContratoForm(forms.ModelForm):
    ips = forms.ModelChoiceField(
        queryset=Profile.objects.filter(role='IPS'),
        required=False, # Set to False since model field is nullable
        label="IPS Asociada"
    )
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    fecha_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    fecha_liquidacion = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    fecha_conciliacion = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    fecha_presupuesto = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    FORMA_PAGO_CHOICES = [
        ('10A - 30PP 60 sp', '10A - 30PP 60 sp'),
        ('30A - 60PP 100 sp', '30A - 60PP 100 sp'), # Example additional choice
        # Add more choices as needed
    ]
    forma_pago = forms.ChoiceField(choices=FORMA_PAGO_CHOICES, required=False)

    class Meta:
        model = Contrato
        fields = [
            'numero',
            'vigencia',
            'tipo_contrato',
            'valor',
            'ips',
            'objeto',
            'fecha_inicio',
            'fecha_fin',
            'supervisor',
            'forma_pago',
            'fecha_liquidacion',
            'fecha_conciliacion',
            'fecha_presupuesto',
            'servicios_cubiertos',
            'tarifario_adjunto',
            'condiciones_pago',
            'adjunto',
            'alerta_vencimiento',
        ]

class TarifaContratoForm(forms.ModelForm):
    class Meta:
        model = TarifaContrato
        fields = '__all__'
        exclude = ['contrato'] # El contrato se asignará desde la vista

class ResolucionForm(forms.ModelForm):
    facturas = forms.ModelMultipleChoiceField(
        queryset=Factura.objects.filter(estado_auditoria__in=['Finalizada', 'Auditada']),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Facturas a incluir en la Resolución (solo facturas Finalizadas o Auditadas)"
    )

    class Meta:
        model = Resolucion
        fields = ['numero_resolucion', 'entidad_territorial', 'nombre_firmante', 'facturas']
        help_texts = {
            'numero_resolucion': 'Número único que identifica la resolución.',
            'entidad_territorial': 'Nombre completo de la Secretaría de Salud que emite la resolución (ej. Secretaría de Salud de Antioquia).',
            'nombre_firmante': 'Nombre completo de la persona que firma la resolución.',
        }

    def clean_facturas(self):
        facturas = self.cleaned_data.get('facturas')
        if not facturas:
            raise ValidationError("Debes seleccionar al menos una factura para la resolución.")

        # Opcional: Podríamos añadir aquí una validación para que todas las facturas sean de la misma IPS,
        # si esto es un requisito para las resoluciones.
        
        return facturas
