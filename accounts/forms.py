from django import forms
from .models import NoDues, Student

class DuesForm(forms.ModelForm):
    class Meta:
        model = NoDues
        fields = ['has_dues', 'due_date', 'remark']

class StudentSearchForm(forms.Form):
    register_number = forms.CharField(label='Register Number', max_length=50)
    branch = forms.CharField(label='Branch', max_length=50)
