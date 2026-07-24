from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Назва")
    color = models.CharField(max_length=7, default='#007bff', verbose_name="HEX колір")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ['name']


class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Зміст")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Теги")
    is_featured = models.BooleanField(default=False, verbose_name="Обрана")
    views = models.PositiveIntegerField(default=0, verbose_name="Перегляди")
    likes = models.PositiveIntegerField(default=0, verbose_name="Вподобання")
    published_at = models.DateTimeField(auto_now_add=True, verbose_name="Опубліковано")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Стаття"
        verbose_name_plural = "Статті"
        ordering = ['-published_at']
