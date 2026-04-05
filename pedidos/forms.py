from django import forms
from .models import Pedido

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['estado', 'telefono', 'direccion', 'numero_guia', 'orden_flete_pdf']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'numero_guia': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Escribe el número de guía aquí...'}),
            'orden_flete_pdf': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'estado': 'Estado del Pedido',
            'telefono': 'Teléfono',
            'direccion': 'Dirección de Entrega',
            'numero_guia': 'Número de Guía',
            'orden_flete_pdf': 'PDF Orden de Flete',
        }
