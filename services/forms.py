from django import forms
from .models import Subcategory, ServiceCategory, Testimonial

class CategoryForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ['name', 'description']

class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = Subcategory
        fields = ['category', 'name', 'description']

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1,
                'max': 10,
                'class': 'form-control',
                'placeholder': 'Rating (1-10)',
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your feedback here...',
                'rows': 4,
            }),
        }