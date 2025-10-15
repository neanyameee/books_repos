import json
import xml.etree.ElementTree as ET
import os
import uuid


def export_to_json(books, file_path):
    data = []
    for book in books:
        data.append({
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn,
            'publication_year': book.publication_year
        })

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def export_to_xml(books, file_path):
    root = ET.Element('books')
    for book in books:
        book_elem = ET.SubElement(root, 'book')
        ET.SubElement(book_elem, 'title').text = book.title
        ET.SubElement(book_elem, 'author').text = book.author
        ET.SubElement(book_elem, 'isbn').text = book.isbn
        ET.SubElement(book_elem, 'publication_year').text = str(book.publication_year)

    tree = ET.ElementTree(root)
    tree.write(file_path, encoding='utf-8', xml_declaration=True)


def import_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    imported_count = 0
    for item in data:
        book, created = Book.objects.get_or_create(
            isbn=item['isbn'],
            defaults={
                'title': item['title'],
                'author': item['author'],
                'publication_year': item.get('publication_year', 2023)
            }
        )
        if created:
            imported_count += 1

    return imported_count


def import_from_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    imported_count = 0
    for book_elem in root.findall('book'):
        isbn = book_elem.find('isbn').text
        title = book_elem.find('title').text
        author = book_elem.find('author').text

        book, created = Book.objects.get_or_create(
            isbn=isbn,
            defaults={
                'title': title,
                'author': author,
                'publication_year': int(book_elem.find('publication_year').text) if book_elem.find(
                    'publication_year') is not None else 2023
            }
        )
        if created:
            imported_count += 1

    return imported_count