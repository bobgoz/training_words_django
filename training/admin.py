from django.contrib import admin

from .models import Word


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    """Админка для слова"""

    # Отображаемые поля в списке
    list_display = (
        'display_word',
        'is_learned',
        'is_active',
        'is_hard',
    )

    # Поля для поиска
    search_fields = (
        'word',
        'definition',
        'example',
        'user__username',
        'user__email',
    )

    # Фильтры
    list_filter = (
        'is_active',
        'is_hard',
        'is_learned',
        'language',
        'user',
        ('created_at', admin.DateFieldListFilter),
    )

    # Поля для сортировки
    ordering = ('-updated_at',)

    # Количество записей на странице
    list_per_page = 25

    # Поля, которые можно редактировать прямо в списке
    list_editable = ('is_active', 'is_hard', 'is_learned')

    # Поля только для чтения
    readonly_fields = (
        'id',
        'created_at',
        'updated_at',
    )

    # Группировка полей в форме редактирования
    fieldsets = (
        (
            'Основная информация',
            {
                'fields': (
                    'user',
                    'word',
                    'definition',
                    'example',
                )
            },
        ),
        (
            'Статусы',
            {
                'fields': (
                    'is_active',
                    'is_hard',
                    'is_learned',
                ),
            },
        ),
        (
            'Система повторений',
            {
                'fields': (
                    'repetition_count',
                    'next_review_date',
                ),
            },
        ),
        (
            'Изображение',
            {
                'fields': ('image',),
            },
        ),
        (
            'Даты',
            {
                'fields': ('created_at', 'updated_at'),
            },
        ),
    )

    @admin.display(description='Слово и принадлежность')
    def display_word(self, obj):
        return obj
