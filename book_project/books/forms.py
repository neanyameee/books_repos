from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'publication_year']

class FileUploadForm(forms.Form):
    file = forms.FileField()
    file_type = forms.ChoiceField(choices=[('json', 'JSON'), ('xml', 'XML')])