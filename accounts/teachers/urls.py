from django.urls import path
from . import views
  # <-- make sure this points to the right views file

# or
# from accounts.students.views import teacher_assignments, view_submissions, delete_assignment

from django.urls import path
from . import views
from accounts.students import views as student_views



urlpatterns = [
    ##path('', views.dashboard, name='teacher_dashboard'),
      path('', views.teacher_dashboard, name='teacher-dashboard'),
    ##path('profile/', views.teacher_profile, name='teacher_profile'),

    #path('profile/', views.view_profile, name='teacher_profile'),
  
    path('profile/', views.teacher_profile, name='teacher_profile'),



    path('add_subject/', views.add_subject, name='add_subject'),
    path('edit_subject/<int:id>/', views.edit_subject, name='edit_subject'),
    path('delete_subject/<int:id>/', views.delete_subject, name='delete_subject'),
  # NEW (correct)
path('teachers/upload-material/', views.upload_and_manage_study_material, name='upload_and_manage_study_material'),
path('teachers/delete-material/<int:material_id>/', views.delete_study_material, name='delete_study_material'),
path('teachers/mark-attendance/', views.mark_attendance, name='mark_attendance'),
   path('assignments/', views.teacher_assignments, name='teacher_assignments'),
    path('assignments/<int:assignment_id>/submissions/', views.view_submissions, name='view_submissions'),
        path('assignments/delete/<int:assignment_id>/', views.delete_assignment, name='delete_assignment'),

    path('chat/', views.teacher_chat, name='teacher_chat'),
    path('teacher/messages/<int:doubt_id>/', views.teacher_doubt_messages, name='teacher_doubt_messages'),
    path('teacher/unread-counts/', views.teacher_unread_counts, name='teacher_unread_counts'),

    
    path('messages/<int:doubt_id>/', student_views.get_messages, name='teacher_get_messages'),
    path('send-message/<int:doubt_id>/', student_views.send_message, name='teacher_send_message'),
   path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),



    
      
]

    

    



    



    







