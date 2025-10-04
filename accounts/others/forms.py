from django import forms
from accounts.models import NoDues

class NoDuesForm(forms.ModelForm):
    class Meta:
        model = NoDues
        fields = ['has_dues', 'due_date', 'remark']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'remark': forms.Textarea(attrs={'rows': 2}),
        }
