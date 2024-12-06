from django import forms
from django.conf import settings
import psycopg2

class CategoryForm(forms.Form):
    name = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)

    def save(self):
        data = self.cleaned_data
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO services_servicecategory (name, description)
                    VALUES (%s, %s)
                """, (data['name'], data['description']))
                conn.commit()

class SubcategoryForm(forms.Form):
    category_id = forms.IntegerField()
    name = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)

    def save(self):
        data = self.cleaned_data
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO services_subcategory (category_id, name, description)
                    VALUES (%s, %s, %s)
                """, (data['category_id'], data['name'], data['description']))
                conn.commit()

class TestimonialForm(forms.Form):
    rating = forms.IntegerField(min_value=1, max_value=10)
    content = forms.CharField(widget=forms.Textarea)
    subcategory_id = forms.IntegerField()
    user_id = forms.IntegerField()

    def save(self):
        data = self.cleaned_data
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO services_testimonial (rating, content, subcategory_id, user_id, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                """, (data['rating'], data['content'], data['subcategory_id'], data['user_id']))
                conn.commit()

class ServiceJobForm(forms.Form):
    category = forms.ChoiceField(choices=[], required=True, label="Service Category")
    subcategory = forms.ChoiceField(choices=[], required=True, label="Service Subcategory")

    def __init__(self, *args, **kwargs):
        category_choices = kwargs.pop('category_choices', [])
        subcategory_choices = kwargs.pop('subcategory_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['category'].choices = category_choices
        self.fields['subcategory'].choices = subcategory_choices