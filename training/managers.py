from django.db import models


class WordManager(models.Manager):
    """Кастомный  менеджер для модели Word"""

    def all_self(self, user):
        return super().get_queryset().filter(user=user) 

    def active(self, user):
        """Только активные слова"""
        return self.all_self(user).filter(is_active=True)

    def hard(self, user):
        """Только сложные слова"""
        return self.all_self(user).filter(is_hard=True)

    def count_active(self, user):
        """Количество активных слов"""
        return self.active(user).count()
    
    def count_hard(self, user):
        """ Количество сложных слов """
        return self.hard(user).count()

    def count_all_words(self, user):
        """Количество всех слов пользователя"""
        return self.all_self(user).count()

    def random_words(self, user, limit):
        """Рандомные слова"""
        return self.all_self(user).order_by('?')[:limit]
