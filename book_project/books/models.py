from django.db import models
import uuid

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13)
    publication_year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.author}"


class ImportedFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_filename = models.CharField(max_length=255)
    stored_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10)
    upload_date = models.DateTimeField(auto_now_add=True)