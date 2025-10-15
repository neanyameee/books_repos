from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
import os
import uuid

from .models import Book, ImportedFile
from .forms import BookForm, FileUploadForm
from .utils import export_to_json, export_to_xml, import_from_json, import_from_xml


def home(request):
    return render(request, 'books/home.html')


def book_list(request):
    books = Book.objects.all()
    return render(request, 'books/book_list.html', {'books': books})


def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()

    return render(request, 'books/add_book.html', {'form': form})


def export_books(request):
    if request.method == 'POST':
        file_type = request.POST.get('file_type')
        books = Book.objects.all()

        if not books.exists():
            return redirect('book_list')

        filename = f"books_export.{file_type}"
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        if file_type == 'json':
            export_to_json(books, file_path)
        elif file_type == 'xml':
            export_to_xml(books, file_path)

        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

        os.remove(file_path)
        return response

    return render(request, 'books/export_books.html')


def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            file_type = form.cleaned_data['file_type']

            filename = f"{uuid.uuid4()}.{file_type}"
            file_path = os.path.join(settings.MEDIA_ROOT, filename)

            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            try:
                if file_type == 'json':
                    imported_count = import_from_json(file_path)
                elif file_type == 'xml':
                    imported_count = import_from_xml(file_path)

                ImportedFile.objects.create(
                    original_filename=uploaded_file.name,
                    stored_filename=filename,
                    file_type=file_type
                )

                return redirect('book_list')

            except Exception as e:
                if os.path.exists(file_path):
                    os.remove(file_path)
                return render(request, 'books/upload_file.html', {
                    'form': form,
                    'error': f'Ошибка: {str(e)}'
                })
    else:
        form = FileUploadForm()

    return render(request, 'books/upload_file.html', {'form': form})