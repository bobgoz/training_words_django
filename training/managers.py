from django.db import models


class WordManager(models.Manager):
    """Кастомный  менеджер для модели Word"""

    def all_self(self, user):
        return super().get_queryset().filter(user=user)

    def is_active(self, user):
        """Только активные слова"""
        return self.all_self(user).filter(is_active=True, is_learned=False)

    def is_not_active(self, user):
        """Только неактивные слова"""
        return self.all_self(user).filter(is_active=False)

    def is_hard(self, user):
        """Только сложные слова"""
        return self.is_active(user).filter(is_hard=True)

    def is_learned(self, user):
        """Только изученные словаз"""
        return self.all_self(user).filter(is_learned=True)

    def count_active(self, user):
        """Количество активных слов"""
        return self.is_active(user).count()

    def count_hard(self, user):
        """Количество сложных слов"""
        return self.is_hard(user).count()

    def count_all_words(self, user):
        """Количество всех слов пользователя"""
        return self.all_self(user).count()

    def random_words(self, user):
        """Рандомные слова"""
        return self.is_active(user).order_by('?')
