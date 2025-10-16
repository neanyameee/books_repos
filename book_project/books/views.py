from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Book
import json, os, uuid
from django.conf import settings


def home(request):
    """Главная страница со всеми функциями"""

    # Создаем папку для файлов
    files_dir = os.path.join(settings.MEDIA_ROOT, 'json_files')
    os.makedirs(files_dir, exist_ok=True)

    # Обработка добавления книги через форму
    if request.method == 'POST' and 'add_book' in request.POST:
        title = request.POST.get('title', '').strip()
        author = request.POST.get('author', '').strip()
        year = request.POST.get('year', '').strip()

        if title and author and year:
            try:
                Book.objects.create(title=title, author=author, year=int(year))
                messages.success(request, 'Книга добавлена!')
            except:
                messages.error(request, 'Ошибка! Проверьте данные.')
        else:
            messages.error(request, 'Заполните все поля!')
        return redirect('home')

    # Обработка экспорта в JSON
    if request.method == 'POST' and 'export_json' in request.POST:
        books = list(Book.objects.values())
        if books:
            filename = f"books_{uuid.uuid4().hex[:8]}.json"
            filepath = os.path.join(files_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(books, f, ensure_ascii=False, indent=2)

            messages.success(request, f'Экспортировано {len(books)} книг в {filename}')
        else:
            messages.warning(request, 'Нет книг для экспорта!')
        return redirect('home')

    # Обработка загрузки JSON файла
    if request.method == 'POST' and 'upload_json' in request.POST:
        file = request.FILES.get('json_file')
        if file and file.name.endswith('.json'):
            # Генерируем безопасное имя
            filename = f"{uuid.uuid4().hex}.json"
            filepath = os.path.join(files_dir, filename)

            try:
                # Сохраняем файл
                with open(filepath, 'wb+') as f:
                    for chunk in file.chunks():
                        f.write(chunk)

                # Валидация JSON
                with open(filepath, 'r', encoding='utf-8') as f:
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

                    messages.success(request, f'Импортировано {imported} книг!')
                else:
                    os.remove(filepath)
                    messages.error(request, 'JSON должен содержать массив объектов!')

            except json.JSONDecodeError:
                os.remove(filepath)
                messages.error(request, 'Невалидный JSON файл!')
            except Exception as e:
                os.remove(filepath)
                messages.error(request, f'Ошибка: {str(e)}')
        else:
            messages.error(request, 'Выберите JSON файл!')
        return redirect('home')

    # Получаем список существующих JSON файлов
    json_files = []
    if os.path.exists(files_dir):
        for f in os.listdir(files_dir):
            if f.endswith('.json'):
                filepath = os.path.join(files_dir, f)
                json_files.append({
                    'name': f,
                    'size': os.path.getsize(filepath),
                    'path': filepath
                })

    context = {
        'books': Book.objects.all(),
        'json_files': json_files,
        'has_books': Book.objects.exists(),
        'has_files': len(json_files) > 0
    }
    return render(request, 'books/home.html', context)


def view_json_file(request, filename):
    """Просмотр содержимого JSON файла"""
    filepath = os.path.join(settings.MEDIA_ROOT, 'json_files', filename)

    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            data = json.loads(content)
            pretty_content = json.dumps(data, ensure_ascii=False, indent=2)

            return render(request, 'books/view_json.html', {
                'filename': filename,
                'content': pretty_content,
                'book_count': len(data) if isinstance(data, list) else 1
            })
        except:
            messages.error(request, 'Ошибка чтения файла!')
    else:
        messages.error(request, 'Файл не найден!')

    return redirect('home')