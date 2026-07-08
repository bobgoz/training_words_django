from django.conf import settings
from django.db import models

from training.mixins import BaseIntervalLogicMixin, BaseTimestampMixin

from training.constants import PHRASE_MAX_LENGTH


class Phrase(
    BaseTimestampMixin,
    BaseIntervalLogicMixin,
):
    """Модель  словосочетания."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
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
