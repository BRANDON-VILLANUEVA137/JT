# Catalogo/forms.py
from django import forms
from .models import Product, Category, Brand

class ProductForm(forms.ModelForm):
    new_category_name = forms.CharField(max_length=100, required=False, label='', help_text='Nombre para nueva categoría (solo admin)', widget=forms.TextInput(attrs={'class': 'form-control mt-1', 'placeholder': 'Nueva categoría...'}))
    new_brand_name = forms.CharField(max_length=100, required=False, label='', help_text='Nombre para nueva marca (solo admin)', widget=forms.TextInput(attrs={'class': 'form-control mt-1', 'placeholder': 'Nueva marca...'}))
    
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'condition', 'category', 'brand', 'stock', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False
        self.fields['brand'].required = False
        self.fields['category'].empty_label = "— Selecciona o crea nueva —"
        self.fields['brand'].empty_label = "— Selecciona o crea nueva —"


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
