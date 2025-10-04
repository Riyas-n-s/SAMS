from django import forms
from accounts.models import Student, Staff, OthersStaff


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['register_number', 'name', 'branch', 'semester', 'roll_number']


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['name', 'staff_id', 'department']


class OthersStaffForm(forms.ModelForm):
    class Meta:
        model = OthersStaff
        fields = ['name', 'staff_id', 'staff_in_charge']


class StudentBulkUploadForm(forms.Form):
    file = forms.FileField(label="Upload CSV File")


class StaffBulkUploadForm(forms.Form):
    file = forms.FileField(label="Select CSV file")


class OthersStaffBulkUploadForm(forms.Form):
    file = forms.FileField(label="Select CSV file")
