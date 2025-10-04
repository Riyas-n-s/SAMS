from django.urls import path, include
from . import views
from accounts.others import views as others_views

urlpatterns = [
        path('', views.home, name='home'),
        path('loader/<str:next_url>/', views.loader_page, name='loader_page'),

 path('privacy/', views.privacy, name='privacy'),
  path('terms/', views.terms, name='terms'),
  path('test/', views.test, name='test'),

          path('contact/', views.contact, name='contact'),
          path('about/', views.about, name='about'),
    path('login', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),

    path('forgot-password-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('set-new-password/', views.set_new_password, name='set_new_password'),

    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('others-dashboard/', views.others_dashboard, name='others_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('get-user-details/', views.get_user_details, name='get_user_details'),

    # NEW: Student dashboard routes
    path('students/', include('accounts.students.urls')),  
    path('teacher/', include('accounts.teachers.urls')),
    path('others/', include('accounts.others.urls')),
      #path('profile/', views.teacher_profile, name='teacher_profile'),
      path('teacher/profile/', views.teacher_profile, name='teacher_profile'),



 
path('admin-panel/', include('accounts.admin_panel.urls')),

]

   

   


