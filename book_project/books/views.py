from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Book
import json, os, uuid
from django.conf import settings


def home(request):
    files_dir = os.path.join(settings.MEDIA_ROOT, 'json_files')
    os.makedirs(files_dir, exist_ok=True)

    # Добавление книги
    if request.method == 'POST' and 'title' in request.POST:
        title = request.POST['title']
        author = request.POST['author']
        year = request.POST['year']
        if title and author and year:
            Book.objects.create(title=title, author=author, year=year)
            messages.success(request, 'Книга добавлена')
        return redirect('home')

    # Экспорт в JSON
    if request.method == 'POST' and 'export' in request.POST:
        books = list(Book.objects.values())
        if books:
            filename = f"books_{uuid.uuid4().hex[:8]}.json"
            filepath = os.path.join(files_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(books, f, indent=2)
            messages.success(request, f'Экспортировано {len(books)} книг')
        return redirect('home')

    # Загрузка JSON
    if request.method == 'POST' and 'json_file' in request.FILES:
        file = request.FILES['json_file']
        if file.name.endswith('.json'):
            filename = f"{uuid.uuid4().hex}.json"
            filepath = os.path.join(files_dir, filename)

            try:
                # Сохраняем файл
                with open(filepath, 'wb+') as f:
                    for chunk in file.chunks():
                        f.write(chunk)

                # Валидируем и импортируем
                with open(filepath, 'r') as f:
                    data = json.load(f)

                if isinstance(data, list):
                    imported = 0
                    for item in data:
                        if all(k in item for k in ['title', 'author', 'year']):
                            Book.objects.get_or_create(
                                title=item['title'],
                                author=item['author'],
                                year=item['year']
                            )
                            imported += 1
                    messages.success(request, f'Импортировано {imported} книг')
                else:
                    os.remove(filepath)
                    messages.error(request, 'Файл должен содержать массив')

            except json.JSONDecodeError:
                os.remove(filepath)
                messages.error(request, 'Неверный формат JSON')
            except Exception as e:
                os.remove(filepath)
                messages.error(request, f'Ошибка: {str(e)}')
        return redirect('home')

    # Список JSON файлов
    json_files = []
    if os.path.exists(files_dir):
        for f in os.listdir(files_dir):
            if f.endswith('.json'):
                filepath = os.path.join(files_dir, f)
                json_files.append({
                    'name': f,
                    'size': os.path.getsize(filepath),
                })

    return render(request, 'books/home.html', {
        'books': Book.objects.all(),
        'json_files': json_files,
    })


def view_json_file(request, filename):
    filepath = os.path.join(settings.MEDIA_ROOT, 'json_files', filename)

    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        data = json.loads(content)
        pretty_content = json.dumps(data, indent=2)

        return render(request, 'books/view_json.html', {
            'filename': filename,
            'content': pretty_content,
        })

    messages.error(request, 'Файл не найден')
    return redirect('home')