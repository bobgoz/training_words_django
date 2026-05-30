from django.db import models
from django.utils import timezone

from .constants import MIN_ACTIVE_WORDS


class WordManager(models.Manager):
    """Кастомный менеджер для модели Word"""

    def all_self(self, user):
        """Все слова пользователя."""
        return super().get_queryset().filter(user=user)

    def is_active(self, user):
        """Только активные слова"""
        return self.all_self(user).filter(is_active=True, is_learned=False)

    def is_not_active(self, user):
        """Только неактивные слова"""
        return self.all_self(user).filter(is_active=False, is_learned=False)

    def is_hard(self, user):
        """Только сложные слова"""
        return self.is_active(user).filter(is_hard=True)

    def is_learned(self, user):
        """Только изученные слова"""
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

    def hard_language_ru(self, user):
        """Сложные русские слова"""
        return self.is_hard(user).filter(language='ru')

    def hard_language_en(self, user):
        """Сложные английские слова"""
        return self.is_hard(user).filter(language='en')

    # ----------Логика интервальных повторений ----------
    def needs_review(self, user):
        """Слова, которые пора повторять"""
        return self.all_self(user).filter(
            next_review_date__lte=timezone.now(), is_active=False
        )

    def due_for_review_count(self, user):
        """Количество слов для повторения сегодня"""
        return self.needs_review(user).count()

    def activate_due_words(self, user):
        """Активирует все слова, время которых пришло"""
        return self.needs_review(user).update(is_active=True)

    def ensure_min_active_words(self, user):
        """
        Обеспечивает минимальное количество активных слов
        и автоматически меняет поле is_learned на False, если количество
        повторений слова меньше определенного.
        """
        active_count = self.is_active(user).count()

        if active_count < MIN_ACTIVE_WORDS:
            # Сколько нужно добавить
            needed = MIN_ACTIVE_WORDS - active_count

            # Берём неактивные, не изученные слова
            # (приоритет слова, обновленные давно)
            ids_to_activate = list(
                self.is_not_active(
                    user,
                )
                .filter(next_review_date__lte=timezone.now())
                .order_by(
                    'updated_at',
                )
                .values_list('id', flat=True)[:needed]
            )

            if ids_to_activate:
                count = self.filter(id__in=ids_to_activate).update(
                    is_active=True,
                )
                return count

        return 0
