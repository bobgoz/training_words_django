"""Модуль с моделями для приложения Phrase."""

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from phrase.managers import PhraseManager
from training.constants import PHRASE_MAX_LENGTH
from training.mixins import (
    BaseIntervalLogicMixin,
    BaseTimestampMixin,
)

from .constants import MIN_ACTIVE_WORDS


class Phrase(
    BaseTimestampMixin,
    BaseIntervalLogicMixin,
):
    """Модель  словосочетания."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    phrase = models.CharField(
        "Словосочетание",
        max_length=PHRASE_MAX_LENGTH,
        help_text="Обязательное поле",
    )

    phrases = PhraseManager()
    objects = models.Manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["phrase", "user"],
                name="unique_phrase_for_user",
            ),
        ]
        verbose_name = "словосочетание"
        verbose_name_plural = "словосочетания"
        ordering = ("-created_at",)

    def get_absolute_url(self):
        """Возвращает аюсолютный юрл объекта."""
        return reverse("phrase_detail", kwargs={"pk_phrase": self.pk})

    def get_text(self):
        """Возвращает словосочетание."""
        return self.phrase

    def __str__(self):
        return f'{self.phrase} -> {self.user}'

    @classmethod
    def ensure_min_active_phrases(cls, user):
        """
        Обеспечивает минимальное количество активных словосочетаний.
        """

        active_count = cls.phrases.is_active(user).count()

        if active_count < MIN_ACTIVE_WORDS:
            # Сколько нужно добавить
            needed = MIN_ACTIVE_WORDS - active_count
            # Приоритет слова, обновленные давно
            ids_to_activate = list(
                cls.phrases.inactive(
                    user,
                )
                .filter(
                    next_review_date__lte=timezone.now(),
                )
                .order_by(
                    "updated_at",
                )
                .values_list("id", flat=True)[:needed]
            )

            if ids_to_activate:
                count = cls.objects.filter(id__in=ids_to_activate).update(
                    is_active=True,
                    is_learned=False,
                )
                return count

        return 0
