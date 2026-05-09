from django import forms
from .models import (
    Lote, MovimientoInventario, UnidadIndividual, 
    ConteoFisico, ConteoFisicoItem, AlertaStock
)
from Catalogo.models import Product


class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['product', 'codigo_lote', 'cantidad_inicial', 'fecha_vencimiento', 
                  'proveedor', 'costo_unitario', 'notas']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'codigo_lote': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: LOTE-001'}),
            'cantidad_inicial': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'proveedor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del proveedor'}),
            'costo_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class MovimientoForm(forms.Form):
    """Formulario para registrar movimientos manuales de inventario."""
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(activo=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Producto'
    )
    TIPO_CHOICES = [
        ('', '--- Selecciona tipo ---'),
        ('entrada_compra', 'Entrada - Compra a proveedor'),
        ('entrada_devolucion', 'Entrada - Devolución de cliente'),
        ('entrada_ajuste', 'Entrada - Ajuste de inventario'),
        ('salida_devolucion_proveedor', 'Salida - Devolución a proveedor'),
        ('salida_merma', 'Salida - Merma/Pérdida'),
        ('salida_ajuste', 'Salida - Ajuste de inventario'),
    ]
    tipo = forms.ChoiceField(choices=TIPO_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), label='Tipo de movimiento')
    cantidad = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        label='Cantidad',
        help_text='Ingresa siempre valores positivos (se registrará como entrada/salida según el tipo)'
    )
    lote = forms.ModelChoiceField(
        queryset=Lote.objects.filter(activo=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Lote (opcional)'
    )
    notas = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Motivo del movimiento...'}),
        label='Notas'
    )

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        cantidad = cleaned_data.get('cantidad')
        product = cleaned_data.get('product')

        if tipo and cantidad and product:
            # Para salidas, verificar stock suficiente
            if tipo.startswith('salida') and cantidad > product.stock:
                raise forms.ValidationError(
                    f'Stock insuficiente. Stock actual: {product.stock}'
                )
        return cleaned_data


class EntradaCompraForm(forms.Form):
    """Formulario rápido para entrada por compra."""
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(activo=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Producto'
    )
    cantidad = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        label='Cantidad'
    )
    proveedor = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del proveedor'}),
        label='Proveedor'
    )
    costo_unitario = forms.DecimalField(
        max_digits=10, decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Opcional'}),
        label='Costo unitario'
    )
    fecha_vencimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Fecha de vencimiento (opcional)'
    )
    codigo_lote = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-generado si se deja vacío'}),
        label='Código de lote (opcional)'
    )


class SalidaMermaForm(forms.Form):
    """Formulario para registrar merma/pérdida."""
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(activo=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Producto'
    )
    cantidad = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        label='Cantidad'
    )
    motivo = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe el motivo de la merma...'}),
        label='Motivo de la merma'
    )

    def clean(self):
        cleaned_data = super().clean()
        cantidad = cleaned_data.get('cantidad')
        product = cleaned_data.get('product')
        if cantidad and product and cantidad > product.stock:
            raise forms.ValidationError(
                f'Stock insuficiente. Stock actual: {product.stock}'
            )
        return cleaned_data


class UnidadIndividualForm(forms.ModelForm):
    class Meta:
        model = UnidadIndividual
        fields = ['product', 'codigo_interno', 'lote', 'estado', 'precio_costo', 'precio_venta', 'notas']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'codigo_interno': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: SN-001'}),
            'lote': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'precio_costo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ConteoFisicoForm(forms.ModelForm):
    class Meta:
        model = ConteoFisico
        fields = ['codigo_conteo', 'fecha_conteo', 'notas']
        widgets = {
            'codigo_conteo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: CON-2024-001'}),
            'fecha_conteo': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ConteoFisicoItemForm(forms.ModelForm):
    class Meta:
        model = ConteoFisicoItem
        fields = ['product', 'stock_contado', 'notas']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'stock_contado': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock_contado'].label = 'Stock contado físicamente'


class AlertaStockForm(forms.ModelForm):
    class Meta:
        model = AlertaStock
        fields = ['product', 'stock_minimo', 'activo']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }