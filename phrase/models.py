"""Модуль с моделями для приложения Phrase."""


from django.conf import settings
from django.db import models
from django.urls import reverse

from training.constants import PHRASE_MAX_LENGTH
from training.mixins import BaseIntervalLogicMixin, BaseTimestampMixin


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
