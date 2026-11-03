"""Модели для наследования.

Содержит модели-миксины для всех приложений,
где требуется логика интервальных повторений.
"""

from datetime import timedelta

from django.db import models
from django.utils import timezone

from .constants import INTERVALS


class BaseIntervalLogicMixin(models.Model):
    """Базовый класс для добавления логики интервальных повторений."""

    active_items_manager_name = None

    repetition_count = models.IntegerField(
        "Количество успешных повторений",
        default=0,
        help_text='Сколько раз пользователь ответил "Знаю"',
    )
    next_review_date = models.DateTimeField(
        "Дата следующего повторения",
        default=timezone.now,
        help_text="Когда слово снова станет активным",
    )

    is_active = models.BooleanField(
        "Активно",
        default=False,
        help_text="Отметьте, если слово должно отображаться в тренировке",
    )
    is_learned = models.BooleanField(
        "Изучено",
        default=False,
        help_text="Отметьте, если слово хорошо усвоили",
    )

    @classmethod
    def ensure_min_active_items(
        cls,
        user,
        min_active_items,
    ):
        """
        Доводит число активных элементов пользователя до заданного минимума.
        """
        if cls.active_items_manager_name is None:
            raise NotImplementedError(
                "В Модели нужно указать active_items_manager_name.",
            )
        manager = getattr(cls, cls.active_items_manager_name)

        active_count = manager.is_active(user).count()
        if active_count >= min_active_items:
            return 0

        needed = min_active_items - active_count
        # Приоритет слова, обновленные давно
        ids_to_activate = list(
            manager.inactive(user)
            .filter(
                next_review_date__lte=timezone.now(),
            )
            .order_by(
                "updated_at",
            )
            .values_list("id", flat=True)[:needed]
        )

        if not ids_to_activate:
            return 0

        return cls.objects.filter(id__in=ids_to_activate).update(
            is_active=True,
            is_learned=False,
        )

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
            # Если пользователь ответил "Не знаю" — сбрасываем прогресс
            self.repetition_count = 0
            # Повтор через час
            self.next_review_date = now + timedelta(hours=1)
            self.is_learned = False
            self.is_active = True

        self.save()

    class Meta:
        abstract = True


class BaseTimestampMixin(models.Model):
    """Класс для добавления меток времени в модели."""

    created_at = models.DateTimeField(
        "Дата и время создания слова",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        "Дата и время обновления слова",
        auto_now=True,
    )

    class Meta:
        abstract = True
