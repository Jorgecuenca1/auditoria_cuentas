from django import forms
from .models import Factura

class FacturaForm(forms.ModelForm):
    fecha_emision = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Factura
        fields = ['numero', 'cufe', 'fecha_emision', 'eps', 'valor_bruto', 'archivo_rips']
