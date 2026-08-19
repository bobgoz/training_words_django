"""Модуль с менеджером модели Phrase."""

from django.db import models
from django.utils import timezone


class PhraseManager(models.Manager):
    """Кастомный менеджер для модели Phrase."""

    def all_self(self, user):
        """Все словосочетания пользователя."""
        return super().get_queryset().filter(user=user)

    def activate_due_words(self, user):
        """Активация истекших словосочетаний."""
        self.is_learned(user).filter(
            next_review_date__lte=timezone.now(),
        ).update(
            is_active=True,
            is_learned=False,
        )

    def is_active(self, user):
        """Только активные словосочетания с активацией просроченных."""
        self.activate_due_words(user)
        ('Активировано!')

        return self.all_self(user).filter(
            is_active=True,
            is_learned=False,
        )

    def inactive(self, user):
        """Только неактивные словосочетания."""
        return self.all_self(user).filter(
            is_active=False,
            is_learned=False,
        )

    def is_learned(self, user):
        """Только изученные словосочетания."""
        return self.all_self(user).filter(is_learned=True)

    def count_inactive(self, user):
        """Количество неактивных словосочетаний."""
        return self.inactive(user).count()

    def count_active(self, user):
        """Количество активных словосочетаний."""
        return self.is_active(user).count()

    def count_all_words(self, user):
        """Количество всех словосочетаний пользователя."""
        return self.all_self(user).count()

    def count_all_learned(self, user):
        """Количество всех изученных словосочетаний."""
        return self.is_learned(user).count()

    # ----------Локализация----------
    def language_ru(self, user):
        """Только русские слова (активные, не изученные)"""
        return self.is_active(user).filter(language="ru")

    def language_en(self, user):
        """Только английские слова (активные, не изученные)"""
        return self.is_active(user).filter(language="en")

    def has_en_words(self, user) -> bool:
        """Возвращает True если есть иностранные слова."""
        return self.all_self(user).filter(language="en").first()
