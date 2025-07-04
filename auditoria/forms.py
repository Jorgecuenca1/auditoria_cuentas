### forms.py
from django import forms
from .models import Glosa, SubtipoGlosa, SubCodigoGlosa
from facturacion.models import Factura

class GlosaForm(forms.ModelForm):
    class Meta:
        model = Glosa
        fields = ['tipo_glosa', 'subtipo_glosa', 'subcodigo_glosa', 'descripcion', 'valor_glosado']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows':2, 'class':'form-control'}),
            'valor_glosado': forms.NumberInput(attrs={'step':'0.01','class':'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subtipo_glosa'].queryset = SubtipoGlosa.objects.none()
        self.fields['subcodigo_glosa'].queryset = SubCodigoGlosa.objects.none()
        if 'tipo_glosa' in self.data:
            try:
                tipo_id = int(self.data.get('tipo_glosa'))
                self.fields['subtipo_glosa'].queryset = SubtipoGlosa.objects.filter(tipo_id=tipo_id)
            except (ValueError, TypeError): pass
        elif self.instance.pk:
            self.fields['subtipo_glosa'].queryset = self.instance.tipo_glosa.subt_glosas
        if 'subtipo_glosa' in self.data:
            try:
                subtipo_id = int(self.data.get('subtipo_glosa'))
                self.fields['subcodigo_glosa'].queryset = SubCodigoGlosa.objects.filter(subtipo_id=subtipo_id)
            except (ValueError, TypeError): pass
        elif self.instance.pk:
            self.fields['subcodigo_glosa'].queryset = self.instance.subtipo_glosa.subcodigos

class TipoAuditoriaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['tipo_auditoria']
        widgets = {
            'tipo_auditoria': forms.Select(attrs={'class': 'form-select form-select-sm', 'label': ''})
        }
