from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

WORD_FIELD_MAX_LENGTH = 150

DEFINITION_FIELD_MAX_LENGTH = 200


class Word(models.Model):
    """Класс слова"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    word = models.CharField(
        'Слово',
        max_length=WORD_FIELD_MAX_LENGTH,
    )

    created_at = models.DateTimeField(
        'Дата и время создания слова',
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        'Дата и время обновления слова',
        auto_now=True,
    )

    is_active = models.BooleanField(
        'Активное слово',
        default=False,
        help_text='Отметьте, если слово должно отображаться в тренировке',
    )
    is_hard = models.BooleanField(
        'Сложное слово',
        default=False,
        help_text='Отметьте, если слово вызывает трудности',
    )
    definition = models.CharField(
        'Определение слова',
        max_length=DEFINITION_FIELD_MAX_LENGTH,
        help_text='Определение слова.'
        f' Количество символов не более {DEFINITION_FIELD_MAX_LENGTH}. '
        'Можно заполнить позже.',
        blank=True,
    )
    example = models.TextField(
        'Пример использования',
        blank=True,
        help_text='Пример использования слова. Можно заполнить позже.'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['word', 'user'],
                name='unique_words_for_user',
            ),
        ]
        verbose_name = 'слово'
        verbose_name_plural = 'слова'
        ordering = ('-created_at',)

    def clean(self):
        """
        Автоматическая заглавная
        буква в начале слова и очистка
        от лишних пробелов.
        """
        self.word = self.word.capitalize().strip()
        self.definition = self.definition.capitalize().strip()
        return super().clean()
