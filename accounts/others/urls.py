from django.urls import path
from .views import others_dashboard
from . import views



urlpatterns = [
   path('dashboard/', views.others_dashboard, name='others_dashboard'),
    path('add-due/', views.add_due, name='add_due'),
    path('clear-dues/', views.clear_all_dues, name='clear_all_dues'),

       

]
    


