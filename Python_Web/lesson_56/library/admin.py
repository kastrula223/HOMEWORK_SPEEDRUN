from django.contrib import admin
from .models import Author, Book, Reader, Loan


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'birth_year']
    list_filter = ['country']
    search_fields = ['name', 'country']
    ordering = ['name']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'pages', 'publication_year', 'is_available']
    list_filter = ['is_available', 'publication_year', 'author']
    search_fields = ['title', 'isbn', 'author__name']
    list_editable = ['is_available']
    ordering = ['-publication_year']


class LoanInline(admin.TabularInline):
    model = Loan
    extra = 1
    readonly_fields = ['loan_date']


@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'total_books']
    search_fields = ['name', 'email']
    ordering = ['name']
    inlines = [LoanInline]

    @admin.display(description="Книг на руках")
    def total_books(self, obj):
        return obj.loan_set.filter(return_date__isnull=True).count()


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['reader', 'book', 'loan_date', 'return_date', 'is_returned']
    list_filter = ['loan_date', 'return_date']
    search_fields = ['reader__name', 'book__title']
    ordering = ['-loan_date']

    @admin.display(description="Повернено", boolean=True)
    def is_returned(self, obj):
        return obj.return_date is not None
