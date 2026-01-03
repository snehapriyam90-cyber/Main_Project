from django import forms
from .models import *

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'category',
            'price',
            'discount_percent',   # ✅ ADD THIS
            'stock',
            'quantity',
            'weight',
            'description',
            'image',
            'is_active'
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product Name'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Price'
            }),
            'discount_percent': forms.NumberInput(attrs={   # ✅ ADD THIS
                'class': 'form-control',
                'placeholder': 'Discount % (optional)',
                'min': 1,
                'max': 90
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Stock Quantity'
            }),
            'quantity' : forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Quantity',
                'min': '1'

            }),
            'weight': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Weight with unit'
            }),


            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your review'}),
        }

class ProductQuestionForm(forms.ModelForm):
    class Meta:
        model = ProductQuestion
        fields = ['question']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ask a question...'})
        }
