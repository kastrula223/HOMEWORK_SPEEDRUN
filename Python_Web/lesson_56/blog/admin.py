import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import Tag, Article


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']
    search_fields = ['name']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'views', 'likes', 'is_featured', 'published_at']
    list_filter = ['is_featured', 'published_at', 'author', 'tags']
    search_fields = ['title', 'content']
    list_editable = ['is_featured']
    filter_horizontal = ['tags']
    readonly_fields = ['views', 'likes']
    actions = ['mark_as_featured', 'reset_views', 'export_selected_articles']

    @admin.action(description="Позначити обрані статті як featured")
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"Позначено як featured: {updated} статей.")

    @admin.action(description="Скинути лічильник переглядів")
    def reset_views(self, request, queryset):
        updated = queryset.update(views=0)
        self.message_user(request, f"Лічильник переглядів скинуто для {updated} статей.")

    @admin.action(description="Експортувати обрані статті у CSV")
    def export_selected_articles(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="articles_export.csv"'

        writer = csv.writer(response)
        writer.writerow(['Заголовок', 'Автор', 'Перегляди', 'Вподобання', 'Featured', 'Опубліковано'])
        for article in queryset:
            writer.writerow([
                article.title,
                article.author.get_username(),
                article.views,
                article.likes,
                'Так' if article.is_featured else 'Ні',
                article.published_at.strftime('%Y-%m-%d %H:%M'),
            ])
        return response
