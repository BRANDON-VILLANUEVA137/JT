from django import forms
from .models import Pedido

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['estado', 'telefono', 'direccion']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'estado': 'Estado del Pedido',
            'telefono': 'Teléfono',
            'direccion': 'Dirección de Entrega',
        }
