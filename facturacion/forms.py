from django import forms
from .models import Factura, Contrato, Paciente, RipsConsulta, RipsMedicamento, RipsProcedimiento, RipsHospitalizacion, RipsOtroServicio, TarifaContrato

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
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    fecha_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Contrato
        fields = '__all__'

class TarifaContratoForm(forms.ModelForm):
    class Meta:
        model = TarifaContrato
        fields = '__all__'
        exclude = ['contrato'] # El contrato se asignará desde la vista
