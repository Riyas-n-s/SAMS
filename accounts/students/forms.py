# forms.py
from django import forms
from accounts.models import Profile

class ProfileCompletionForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['dob', 'email', 'address', 'phone', 'branch', 'semester', 'gender']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.TextInput(attrs={'class': 'form-control'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
