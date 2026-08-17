"""Модуль содержащий настройки админки приложения Phrase."""

from django.contrib import admin

from .models import Phrase


@admin.register(Phrase)
class PhraseAdmin(admin.ModelAdmin):
    """Админка приложения Phrase."""

    # Отображаемые поля в списке
    list_display = (
        "display_phrase",
        "is_learned",
        "is_active",
    )

    # Поля для поиска
    search_fields = (
        "phrase",
        "user__username",
        "user__email",
    )

    # Фильтры
    list_filter = (
        "is_active",
        "is_learned",
        "user",
        ("created_at", admin.DateFieldListFilter),
    )

    # Поля для сортировки
    ordering = ("-updated_at",)

    # Количество записей на странице
    list_per_page = 25

    # Поля, которые можно редактировать прямо в списке
    list_editable = ("is_active", "is_learned")

    # Поля только для чтения
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    # Группировка полей в форме редактирования
    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "user",
                    "phrase",
                )
            },
        ),
        (
            "Статусы",
            {
                "fields": (
                    "is_active",
                    "is_learned",
                ),
            },
        ),
        (
            "Система повторений",
            {
                "fields": (
                    "repetition_count",
                    "next_review_date",
                ),
            },
        ),
        (
            "Даты",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    @admin.display(description="Словосочетание и принадлежность.")
    def display_phrase(self, obj):
        return obj
