from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('upgrade-semesters/', views.upgrade_semesters, name='upgrade_semesters'),
     path("add_student/", views.add_student, name="add_student"),
    path("bulk-upload_students/", views.bulk_upload_students, name="bulk_upload_students"),
    path("students/<int:pk>/edit/", views.edit_student, name="edit_student"),
    path("students/<int:pk>/delete/", views.delete_student, name="delete_student"),
    path('manage-staff/', views.manage_all_staff, name='manage_all_staff'),
    path('staff/edit/<int:staff_id>/', views.edit_staff, name='edit_staff'),
    path('staff/delete/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    path('others/edit/<int:others_id>/', views.edit_others_staff, name='edit_others_staff'),
    path('others/delete/<int:others_id>/', views.delete_others_staff, name='delete_others_staff'),

path('staff/add/', views.add_staff, name='add_staff'),
    path('others-staff/add/', views.add_others_staff, name='add_others_staff'),

    # Bulk CSV Upload
    path('staff/upload-csv/', views.upload_staff_csv, name='staff_csv'),
    path('others-staff/upload-csv/', views.upload_others_staff_csv, name='upload_others_staff_csv'),
    # admin_panel/urls.py
path('a/', views.a, name='a'),

]