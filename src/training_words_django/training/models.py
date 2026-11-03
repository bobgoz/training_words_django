import logging
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone

from training_words_django.learning.model_mixins import (
    BaseIntervalLogicMixin,
    BaseTimestampMixin,
)

from .constants import (
    DEFINITION_FIELD_MAX_LENGTH,
    WORD_FIELD_MAX_LENGTH,
)
from .managers import WordManager
from .services import image_unique_name, translator

User = get_user_model()

logger = logging.getLogger(__name__)


class Word(
    BaseIntervalLogicMixin,
    BaseTimestampMixin,
):
    """Класс слова"""

    active_items_manager_name = "words"

    LANGUAGE_CHOICES = [
        ("en", "Английское"),
        ("ru", "Русское"),
        ("unknown", "Не определено"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    word = models.CharField(
        "Слово",
        max_length=WORD_FIELD_MAX_LENGTH,
        help_text="Обязательное поле",
    )

    definition = models.CharField(
        "Определение слова",
        max_length=DEFINITION_FIELD_MAX_LENGTH,
        help_text="Определение слова."
        f" Количество символов не более {DEFINITION_FIELD_MAX_LENGTH}. "
        "Можно заполнить позже.",
        blank=True,
        null=True,
    )
    example = models.TextField(
        "Пример использования",
        blank=True,
        null=True,
        help_text="Пример использования слова. Можно заполнить позже.",
    )
    language = models.CharField(
        "Язык слова",
        choices=LANGUAGE_CHOICES,
        max_length=10,
    )
    image = models.ImageField(
        "Изображение",
        upload_to=image_unique_name,
        blank=True,
        null=True,
        help_text="Загрузить изображение для слова",
    )

    words = WordManager()
    objects = models.Manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["word", "user"],
                name="unique_words_for_user",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "next_review_date"]),
            models.Index(fields=["user", "is_active"]),
        ]

        verbose_name = "слово"
        verbose_name_plural = "слова"
        # ordering = ("-updated_at",)
        ordering = ("word",)

    def clean(self):
        """
        Автоматическая заглавная
        буква в начале слова и очистка
        от лишних пробелов.

        Добавление перевода для английского слова.
        """
        if self.word:
            self.word = self.word.capitalize().strip()
            if not self.definition and self._detect_language() == "en":
                self.definition = translator(self.word)
        if self.definition:
            self.definition = self.definition.capitalize().strip()
        if self.example:
            self.example = self.example.capitalize().strip()

        return super().clean()

    def __str__(self):
        return f"{self.word} -> {self.user}"

    def _detect_language(self) -> str:
        """Определяет язык слова"""
        if re.search("[а-яА-ЯёЁ]", self.word):
            return "ru"
        return "en"

    def save(self, *args, **kwargs):
        """Изменение данных перед сохранением.

        Назначает перевод слова, если пользователь не передал свой перевод.
        """
        self.language = self._detect_language()
        return super().save(*args, **kwargs)

    @property
    def is_due_for_review(self) -> bool:
        """Проверяет, что дата повторения в будущем"""
        return self.next_review_date and self.next_review_date > timezone.now()

    def get_absolute_url(self):
        """Возвращает абсолютный url объекта."""
        return reverse("detail", kwargs={"pk_word": self.pk})

    def get_text(self):
        """Возвращает слово."""
        return self.word

    @property
    def safe_image_url(self):
        """Безопасное получение URL картинки."""
        if not self.image:
            return None
        try:
            if self.image.storage.exists(self.image.name):
                return self.image.url
        except Exception:
            # Если файл не найден - очищаем поле в БД
            self.image = None
            self.save(update_fields=["image"])
        return None


class TrainingSession(models.Model):
    """Сессия тренировки"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
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
        return f'{self.user} - {self.started_at.strftime("%d.%m.%Y %H:%M")}'
