from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Word


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    """Админка для слова"""

    # Отображаемые поля в списке
    list_display = (
        'id',
        'word_link',
        'user_link',
        'status_badges',
        'is_learned',
        'is_active',
        'is_hard',
        'repetition_progress',
        'next_review_date',
        'created_at_short',
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
        'repetition_count',
        'image_preview',
        'language_display',
    )

    # Группировка полей в форме редактирования
    fieldsets = (
        (
            'Основная информация',
            {
                'fields': (
                    'user',
                    'word',
                    'language_display',
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
                    'status_badges_display',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            'Система повторений',
            {
                'fields': (
                    'repetition_count',
                    'next_review_date',
                    'repetition_progress_bar',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            'Изображение',
            {
                'fields': ('image', 'image_preview'),
                'classes': ('collapse',),
            },
        ),
        (
            'Даты',
            {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',),
            },
        ),
    )

    def word_link(self, obj):
        """Ссылка на слово в админке"""
        url = reverse('admin:training_word_change', args=[obj.id])
        return format_html(
            '<a href="{}"><strong>{}</strong></a>', url, obj.word
        )

    word_link.short_description = 'Слово'
    word_link.admin_order_field = 'word'

    def user_link(self, obj):
        """Ссылка на пользователя"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    user_link.short_description = 'Пользователь'
    user_link.admin_order_field = 'user__username'

    def status_badges(self, obj):
        """Цветные бейджи статусов"""
        badges = []
        if obj.is_active:
            badges.append(
                '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">✅ Активно</span>'
            )
        else:
            badges.append(
                '<span style="background: #6c757d; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">⏸️ Неактивно</span>'
            )

        if obj.is_hard:
            badges.append(
                '<span style="background: #ffc107; color: #000; padding: 2px 8px; border-radius: 12px; font-size: 11px;">⚡ Сложное</span>'
            )

        if obj.is_learned:
            badges.append(
                '<span style="background: #17a2b8; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">📚 Изучается</span>'
            )

        return format_html(' '.join(badges))

    status_badges.short_description = 'Статусы'

    def repetition_progress(self, obj):
        """Прогресс повторений"""
        intervals = [1, 3, 7, 14, 30, 60, 90, 180, 365]
        max_count = len(intervals)
        current = (
            obj.repetition_count
            if obj.repetition_count <= max_count
            else max_count
        )

        percent = (current / max_count) * 100
        bar = format_html(
            '<div style="background: #e9ecef; border-radius: 10px; overflow: hidden; width: 100px; display: inline-block;">'
            '<div style="background: #28a745; width: {}%; height: 6px;"></div>'
            '</div>',
            percent,
        )
        return format_html('{} {}/{}', bar, current, max_count)

    repetition_progress.short_description = 'Прогресс повторений'

    def repetition_progress_bar(self, obj):
        """Прогресс-бар для формы редактирования"""
        intervals = [1, 3, 7, 14, 30, 60, 90, 180, 365]
        max_count = len(intervals)
        current = (
            obj.repetition_count
            if obj.repetition_count <= max_count
            else max_count
        )
        percent = (current / max_count) * 100

        return format_html(
            '<div style="background: #e9ecef; border-radius: 10px; overflow: hidden;">'
            '<div style="background: #28a745; width: {}%; padding: 8px; color: white; text-align: center;">'
            '{}% ({} из {} повторений)</div></div>',
            percent,
            round(percent, 1),
            current,
            max_count,
        )

    repetition_progress_bar.short_description = 'Прогресс повторений'

    def created_at_short(self, obj):
        """Короткая дата создания"""
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    created_at_short.short_description = 'Создано'
    created_at_short.admin_order_field = 'created_at'

    def image_preview(self, obj):
        """Превью изображения"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 150px; max-height: 150px; border-radius: 8px;" />',
                obj.image.url,
            )
        return '—'

    image_preview.short_description = 'Превью изображения'

    def language_display(self, obj):
        """Отображение языка"""
        languages = {
            'ru': '🇷🇺 Русский',
            'en': '🇬🇧 Английский',
            'unknown': '❓ Не определён',
        }
        return languages.get(obj.language, obj.language)

    language_display.short_description = 'Язык'

    def status_badges_display(self, obj):
        """Отображение статусов в форме"""
        return self.status_badges(obj)

    status_badges_display.short_description = 'Текущие статусы'

    # Действия
    actions = ['make_active', 'make_inactive', 'make_hard', 'make_learned']

    def make_active(self, request, queryset):
        """Сделать слова активными"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Активировано {updated} слов.')

    make_active.short_description = 'Сделать активными'

    def make_inactive(self, request, queryset):
        """Сделать слова неактивными"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Деактивировано {updated} слов.')

    make_inactive.short_description = 'Сделать неактивными'

    def make_hard(self, request, queryset):
        """Отметить как сложные"""
        updated = queryset.update(is_hard=True)
        self.message_user(request, f'Отмечено {updated} слов как сложные.')

    make_hard.short_description = 'Отметить как сложные'

    def make_learned(self, request, queryset):
        """Отметить как изучаемые"""
        updated = queryset.update(is_learned=True, is_active=False)
        self.message_user(request, f'Отмечено {updated} слов как изучаемые.')

    make_learned.short_description = 'Перевести в режим изучения'

    # Сохранение с дополнительной логикой
    def save_model(self, request, obj, form, change):
        """При сохранении в админке корректируем дату повторения"""
        if obj.is_learned and obj.is_active:
            obj.is_active = False
        super().save_model(request, obj, form, change)
