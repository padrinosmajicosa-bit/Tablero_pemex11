from django import forms
from .models import Proyecto


class ProyectoForm(forms.ModelForm):
    # 📌 Desplegable para Tipo de Proyecto (Se maneja en Python, no en la BD)
    TIPO_CHOICES = [
        ('RCN', 'RCN'),
        ('SR', 'SR'),
        ('BACKLOG', 'Backlog'),
        ('RCN_ACTIVO', 'RCN Activo'),
    ]
    tipo_proyecto = forms.ChoiceField(
        choices=TIPO_CHOICES,
        label="Tipo de Proyecto",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    # 📌 Campo único para ingresar el folio (RCN-2026-A, SR-102, etc.)
    folio = forms.CharField(
        required=False,
        label="Folio / ID (opcional)",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ej. RCN-2026-A o SR-102"
        })
    )

    # 📌 Desplegables para Estado y Prioridad
    ESTADO_CHOICES = [
        ('inicial', 'Inicial'),
        ('en_proceso', 'En Proceso'),
        ('concluido', 'Concluido'),
        ('cancelado', 'Cancelado'),
    ]
    estado = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    PRIORIDAD_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]
    prioridad = forms.ChoiceField(
        choices=PRIORIDAD_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = Proyecto
        fields = [
            "proyecto",
            "responsable",
            "fase",
            "fecha_inicio",
            "fecha_fin",
        ]
        widgets = {
            "proyecto": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del proyecto..."}),
            "responsable": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del responsable..."}),
            "fase": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Análisis, Desarrollo, Pruebas..."}),
            "fecha_inicio": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "fecha_fin": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si editamos un registro existente, autocompletamos 'tipo_proyecto', 'folio', 'estado' y 'prioridad'
        if self.instance and self.instance.pk:
            if self.instance.rcn:
                self.fields['tipo_proyecto'].initial = 'RCN'
                self.fields['folio'].initial = self.instance.rcn
            elif self.instance.sr:
                self.fields['tipo_proyecto'].initial = 'SR'
                self.fields['folio'].initial = self.instance.sr
            elif self.instance.estado == 'en_proceso':
                self.fields['tipo_proyecto'].initial = 'RCN_ACTIVO'
            else:
                self.fields['tipo_proyecto'].initial = 'BACKLOG'

            self.fields['estado'].initial = self.instance.estado or 'inicial'
            self.fields['prioridad'].initial = self.instance.prioridad or 'media'

    def save(self, commit=True):
        instance = super().save(commit=False)
        tipo = self.cleaned_data.get('tipo_proyecto')
        folio_val = self.cleaned_data.get('folio', '').strip()

        # Asignamos los campos a las columnas reales de la base de datos
        instance.estado = self.cleaned_data.get('estado')
        instance.prioridad = self.cleaned_data.get('prioridad')

        if tipo == 'RCN':
            instance.rcn = folio_val
            instance.sr = None
        elif tipo == 'SR':
            instance.sr = folio_val
            instance.rcn = None
        elif tipo == 'BACKLOG':
            instance.rcn = None
            instance.sr = None
            instance.estado = 'inicial'
        elif tipo == 'RCN_ACTIVO':
            instance.rcn = None
            instance.sr = None
            instance.estado = 'en_proceso'

        if commit:
            instance.save()
        return instance