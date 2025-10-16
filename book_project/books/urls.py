from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('file/<str:filename>/', views.view_json_file, name='view_json'),
]