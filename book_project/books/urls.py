from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.add_book, name='add_book'),
    path('export/', views.export_books, name='export_books'),
    path('upload/', views.upload_file, name='upload_file'),
]