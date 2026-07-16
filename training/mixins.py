from datetime import timedelta

from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.db import models
from django.http import Http404
from django.utils import timezone
from django.views.generic import ListView

from .constants import INTERVALS


class WordAcessMixin(AccessMixin):
    """
    Проверка доступа к слову.
    Если объект не принадлежит пользователю, возвращается ошибка 404.
    """

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != request.user:
            raise Http404("Запрашиваемого слова не существует.")
        return super().dispatch(request, *args, **kwargs)


class BaseShowingViewMixin(LoginRequiredMixin, ListView):
    """Общий класс для всех вью для показа различных типов слов."""

    template_name = "training/word_list.html"
    context_object_name = "words"
    paginate_by: int | None = 10
    page_title = None
    empty_message = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.page_title is None:
            raise NotImplementedError(
                f"Класс {self.__class__.__name__} должен определить "
                "атрибут page_title при наследовании."
            )
        if self.empty_message is None:
            raise NotImplementedError(
                f"Класс {self.__class__.__name__} должен определить "
                "атрибут empty_message при наследовании."
            )
        context["page_title"] = self.page_title
        context["empty_message"] = self.empty_message
        return context


class BaseIntervalLogicMixin(models.Model):
    """Базовый класс для добавления логики интервальных повторений."""

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
            # Если ответил "Не знаю" — сбрасываем прогресс
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
