from django.contrib import admin

from .models import Word


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    """Админка для слова"""

    list_display = (
        'id',
        'user',
        'word',
        'created_at',
        'updated_at',
        'is_active',
        'is_hard',
        'is_learned',
        'definition',
        'example',
        'image',
    )
    search_fields = (
        'word',
        'definition',
    )
    list_filter = ('is_active', 'is_hard', 'user')

