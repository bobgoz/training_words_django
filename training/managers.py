from django.db import models
from django.utils import timezone


class WordManager(models.Manager):
    """Кастомный менеджер для модели Word"""

    def all_self(self, user):
        """Все слова пользователя."""
        return super().get_queryset().filter(user=user)

    def activate_due_words(self, user):
        """Активация истекших слов"""
        self.is_learned(user).filter(
            next_review_date__lte=timezone.now(),
        ).update(
            is_active=True,
            is_learned=False,
        )

    def is_active(self, user):
        """Только активные слова с активацией просроченных"""
        self.activate_due_words(user)

        return self.all_self(user).filter(
            is_active=True,
            is_learned=False,
        )

    def is_not_active(self, user):
        """Только неактивные слова"""
        return self.all_self(user).filter(
            is_active=False,
            is_learned=False,
        )

    def is_hard(self, user):
        """Только сложные слова"""
        return self.is_active(user).filter(is_hard=True)

    def is_learned(self, user):
        """Только изученные слова"""
        return self.all_self(user).filter(is_learned=True)

    def count_inactive(self, user):
        """Количество неактивные слова"""
        return (
            self.all_self(user)
            .filter(
                is_active=False,
                is_learned=False,
            )
            .count()
        )

    def count_active(self, user):
        """Количество активных слов"""
        return self.is_active(user).count()

    def count_hard(self, user):
        """Количество сложных слов"""
        return self.is_hard(user).count()

    def count_all_words(self, user):
        """Количество всех слов пользователя"""
        return self.all_self(user).count()

    def count_all_learned(self, user):
        """Количество всех изученных слов"""
        return self.is_learned(user).count()

    def random_words(self, user):
        """Рандомные слова"""
        return self.is_active(user).order_by('?')

    # ----------Локализация----------
    def language_ru(self, user):
        """Только русские слова (активные, не изученные)"""
        return self.is_active(user).filter(language='ru')

    def language_en(self, user):
        """Только английские слова (активные, не изученные)"""
        return self.is_active(user).filter(language='en')

    def has_en_words(self, user) -> bool:
        """Возвращает True если есть иностранные слова."""
        return self.all_self(user).filter(language='en').first()
