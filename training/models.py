import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from .constants import (
    DEFINITION_FIELD_MAX_LENGTH,
    INTERVALS,
    MIN_ACTIVE_WORDS,
    WORD_FIELD_MAX_LENGTH,
)
from .managers import WordManager
from .service import translator

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
    )
    image = models.ImageField(
        'Изображение',
        upload_to='images/',
        blank=True,
        null=True,
        help_text='Загрузить изображение для слова',
    )

    repetition_count = models.IntegerField(
        'Количество успешных повторений',
        default=0,
        help_text='Сколько раз пользователь ответил "Знаю"',
    )
    next_review_date = models.DateTimeField(
        'Дата следующего повторения',
        default=timezone.now,
        help_text='Когда слово снова станет активным',
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
        indexes = [
            models.Index(fields=['user', 'next_review_date']),
            models.Index(fields=['user', 'is_active']),
        ]

        verbose_name = 'слово'
        verbose_name_plural = 'слова'
        ordering = ('-updated_at',)

    def clean(self):
        """
        Автоматическая заглавная
        буква в начале слова и очистка
        от лишних пробелов.

        Добавление перевода для английского слова.
        """
        self.word = self.word.capitalize().strip()
        if self.definition:
            self.definition = self.definition.capitalize().strip()
        if self.example:
            self.example = self.example.capitalize().strip()
        if not self.definition and self._detect_language() == 'en':
            self.definition = translator(self.word)

        return super().clean()

    def __str__(self):
        return f'{self.word} -> {self.user}'

    def _detect_language(self) -> str:
        """Определяет язык слова"""
        if re.search('[а-яА-ЯёЁ]', self.word):
            return 'ru'
        return 'en'

    def save(self, *args, **kwargs):
        self.language = self._detect_language()
        return super().save(*args, **kwargs)

    def update_review_schedule(self, was_correct):
        """Обновляет расписание повторений на основе ответа пользователя"""
        now = timezone.now()

        if was_correct:
            # Увеличиваем счётчик повторений
            self.repetition_count += 1

            # Интервалы в днях: 1, 3, 7, 14, 30, 60, 90, 180, 365
            intervals = INTERVALS
            idx = min(self.repetition_count - 1, len(intervals) - 1)
            interval_days = intervals[idx]

            # Устанавливаем дату следующего повторения
            self.next_review_date = now + timedelta(days=interval_days)
            self.is_learned = True  # Слово помечается как изученное
            self.is_active = False
        else:
            # Если ответил "Не знаю" — сбрасываем прогресс
            self.repetition_count = 0
            self.next_review_date = now + timedelta(
                hours=1
            )  # Повтор через час
            self.is_learned = False
            self.is_active = True

        self.save()

    @classmethod
    def ensure_min_active_words(cls, user):
        """
        Обеспечивает минимальное количество активных слов.
        """

        active_count = cls.words.is_active(user).count()

        if active_count < MIN_ACTIVE_WORDS:
            # Сколько нужно добавить
            needed = MIN_ACTIVE_WORDS - active_count

            # Приоритет слова, обновленные давно
            ids_to_activate = list(
                cls.words.is_not_active(
                    user,
                )
                .filter(
                    next_review_date__lte=timezone.now(),
                )
                .order_by(
                    'updated_at',
                )
                .values_list('id', flat=True)[:needed]
            )

            if ids_to_activate:
                count = cls.objects.filter(id__in=ids_to_activate).update(
                    is_active=True,
                    is_learned=False,
                )
                return count

        return 0

    @property
    def is_due_for_review(self) -> bool:
        """Проверяет, что дата повторения в будущем"""
        return self.next_review_date and self.next_review_date > timezone.now()


class TrainingSession(models.Model):
    """Сессия тренировки"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    total_words = models.IntegerField(default=0)
    correct_words = models.IntegerField(default=0)
    incorrect_words = models.IntegerField(default=0)

    @property
    def accuracy(self):
        return (
            round(self.correct_words / self.total_words * 100, 1)
            if self.total_words > 0
            else 0
        )

    def __str__(self):
        return f'{self.user} - {self.started_at.strftime('%d.%m.%Y %H:%M')}'


class WordAttempt(models.Model):
    """Хранение ответов пользователя."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    session = models.ForeignKey(
        TrainingSession, on_delete=models.CASCADE, null=True, blank=True
    )
    is_correct = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-attempted_at',)
