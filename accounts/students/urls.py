from django.urls import path
from . import views

from .views import check_dues

urlpatterns = [
    path('', views.dashboard, name='student_dashboard'),
    path('profile/', views.profile, name='student_profile'),
    path('student/study-materials/', views.student_study_materials, name='student_study_materials'),
    path('student/unseen-materials/', views.student_unseen_materials, name='student_unseen_materials'),
    path('resources/', views.student_resources, name='student_resources'),

    path('student/view-attendance/', views.view_attendance, name='view_attendance'),
        path('assignments/', views.student_assignments, name='student_assignments'),
        path('student/unseen-assignments/', views.student_unseen_assignments, name='student_unseen_assignments'),

         path('complete-profile/', views.complete_profile, name='complete_profile'),


    
    path('chat/', views.student_chat, name='student_chat'),
    path('student/unread-doubts/', views.student_unread_doubts, name='student_unread_doubts'),  # <-- add this
    path('create-doubt/', views.create_doubt, name='create_doubt'),
    path('messages/<int:doubt_id>/', views.get_messages, name='get_messages'),
    path('send-message/<int:doubt_id>/', views.send_message, name='send_message'),
     path('delete-doubt/<int:doubt_id>/', views.delete_doubt, name='delete_doubt'),
     path("doubt/unsend/<int:message_id>/", views.unsend_doubt_message, name="unsend_doubt_message"),


    ##path('enter-reg-no/', views.enter_reg_no, name='enter_reg_no'),
    path('check-dues/', check_dues, name='check_dues'),
    path('unseen-dues/', views.student_unseen_dues, name='student_unseen_dues'),
path('download-certificate/', views.download_certificate, name='download_certificate'),



path("cgpa/", views.cgpa_calculator, name="cgpa_calculator"),
    path("save-sgpa/", views.save_sgpa, name="save_sgpa"),  # new endpoint
     path("cgpa/clear/", views.clear_cgpa, name="clear_cgpa"),
]
