from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    """
    Форма для создания и редактирования продукта
    """
    class Meta:
        model = Product
        fields = ['name', 'protein', 'fat', 'carbs', 'weight']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Куриная грудка'
            }),
            'protein': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'fat': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'carbs': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0.1',
                'value': '100'
            }),
        }
        labels = {
            'name': 'Название продукта',
            'protein': 'Белки (на 100г)',
            'fat': 'Жиры (на 100г)',
            'carbs': 'Углеводы (на 100г)',
            'weight': 'Вес порции (г)',
        }
        help_texts = {
            'protein': 'г на 100 грамм продукта',
            'fat': 'г на 100 грамм продукта',
            'carbs': 'г на 100 грамм продукта',
            'weight': 'Укажите вес употребляемой порции',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        protein = cleaned_data.get('protein', 0)
        fat = cleaned_data.get('fat', 0)
        carbs = cleaned_data.get('carbs', 0)
        
        if protein < 0 or fat < 0 or carbs < 0:
            raise forms.ValidationError('Значения не могут быть отрицательными')
        
        return cleaned_data