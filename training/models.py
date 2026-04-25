from django.db import models
from django.contrib.auth import get_user_model
import re

from .managers import WordManager
from .constants import DEFINITION_FIELD_MAX_LENGTH, WORD_FIELD_MAX_LENGTH

User = get_user_model()


class Word(models.Model):
    """Класс слова"""

    LANGUAGE_CHOICES = [
        ('en', 'Английское'),
        ('ru', 'Русское'),
        ('unknown', 'Не определено'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    word = models.CharField(
        'Слово',
        max_length=WORD_FIELD_MAX_LENGTH,
        help_text='Обязательное поле',
    )

    created_at = models.DateTimeField(
        'Дата и время создания слова',
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        'Дата и время обновления слова',
        auto_now=True,
        null=True,
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
    is_learned = models.BooleanField(
        'Изученное слово',
        default=False,
        help_text='Отметьте, если слово хорошо усвоили',
    )
    definition = models.CharField(
        'Определение слова',
        max_length=DEFINITION_FIELD_MAX_LENGTH,
        help_text='Определение слова.'
        f' Количество символов не более {DEFINITION_FIELD_MAX_LENGTH}. '
        'Можно заполнить позже.',
        blank=True,
        null=True,
    )
    example = models.TextField(
        'Пример использования',
        blank=True,
        null=True,
        help_text='Пример использования слова. Можно заполнить позже.',
    )
    language = models.CharField(
        'Язык слова',
        choices=LANGUAGE_CHOICES,
        max_length=10,
        blank=True,
        null=True,
    )
    image = models.ImageField(
        'Изображение',
        upload_to='images/',
        blank=True,
        null=True,
        help_text='Загрузить изображение для слова',
    )

    words = WordManager()
    objects = models.Manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['word', 'user'],
                name='unique_words_for_user',
            ),
        ]
        verbose_name = 'слово'
        verbose_name_plural = 'слова'
        ordering = ('-updated_at',)

    def clean(self):
        """
        Автоматическая заглавная
        буква в начале слова и очистка
        от лишних пробелов.
        """
        self.word = self.word.capitalize().strip()
        if self.definition:
            self.definition = self.definition.capitalize().strip()
        if self.example:
            self.example = self.example.strip()

        return super().clean()

    def __str__(self):
        return f'{self.word}, -> {self.user}'

    def _detect_language(self) -> str:
        """Определяет язык слова"""
        if re.search('[а-яА-ЯёЁ]', self.word):
            return 'ru'
        return 'en'

    def save(self, *args, **kwargs):
        self.language = self._detect_language()
        return super().save(*args, **kwargs)
