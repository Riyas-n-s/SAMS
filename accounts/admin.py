from django.contrib import admin
from .models import Profile, Staff,Student

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'name', 'branch', 'semester', 'register_number', 'phone', 'department')
    list_filter = ('role', 'branch', 'semester')
    search_fields = ('user__username', 'name', 'register_number')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'staff_id', 'department')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'register_number', 'branch', 'semester')
    search_fields = ('name', 'register_number', 'branch')



from django.contrib import admin
from .models import NoDues

admin.site.register(NoDues)  # ← This line is required



from django.contrib import admin
from accounts.models import OthersStaff

@admin.register(OthersStaff)
class OthersStaffAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'name', 'staff_in_charge')
    search_fields = ('staff_id', 'name', 'staff_in_charge')
    list_filter = ('staff_in_charge',)
