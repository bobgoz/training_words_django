from random import shuffle

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    TemplateView,
    UpdateView,
)

from .forms import (
    CreateWordForm,
    EditWordForm,
    TrainingSettingsForm,
)
from .mixins import (
    BaseShowingViewMixin,
    GetSuccessUrlMixin,
    NextUrlMixin,
    WordAcessMixin,
)
from .models import TrainingSession, Word
from .services import clean_session


class WordCreateView(LoginRequiredMixin, CreateView):
    """Вью для создания слов"""

    model = Word
    template_name = "training/create_word.html"
    form_class = CreateWordForm
    success_url = reverse_lazy("add_word")

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Слово добавлено!")
            return response
        except IntegrityError:
            word = form.cleaned_data["word"]
            messages.warning(
                self.request,
                f"Слово {word} уже существует!",
            )
            return self.form_invalid(form)


class ShowActiveWordsView(BaseShowingViewMixin):
    """Вью для отображения активных слов."""

    page_title = "Активные слова (участвуют в тренировке)"
    empty_message = "Нет активных слов"

    def get_queryset(self):
        """Возвращает список активных слов"""
        return Word.words.is_active(self.request.user)

    def get_context_data(self, **kwargs):
        """Передача count_words в контекст."""
        context = super().get_context_data(**kwargs)
        context["count_words"] = Word.words.count_active(self.request.user)
        return context


class ShowInactiveWordsView(BaseShowingViewMixin):
    """Вью для отображения новых слов"""

    page_title = "Новые слова, в ожидании изучения"
    empty_message = "Нет новых слов"

    def get_queryset(self):
        """Возвращает список неактивных слов"""
        return Word.words.is_not_active(self.request.user)

    def get_context_data(self, **kwargs):
        kwargs["count_words"] = Word.words.count_inactive(self.request.user)
        return super().get_context_data(**kwargs)


class ShowLearnedView(BaseShowingViewMixin):
    """Вью для просмотра выученных слов."""

    page_title = "Выученные слова"
    empty_message = "Нет выученных слов"

    def get_queryset(self):
        """Возвращает список выученных слов"""
        return Word.words.is_learned(self.request.user).order_by(
            "next_review_date",
        )

    def get_context_data(self, **kwargs):
        kwargs["count_words"] = Word.words.count_all_learned(self.request.user)
        return super().get_context_data(**kwargs)


class DetailWordView(
    LoginRequiredMixin,
    WordAcessMixin,
    NextUrlMixin,
    DetailView,
):
    """Вью для детального отображения"""

    model = Word
    template_name = "training/detail_word.html"
    pk_url_kwarg = "pk_word"


class DeleteWordView(
    LoginRequiredMixin,
    WordAcessMixin,
    GetSuccessUrlMixin,
    DeleteView,
):
    """Вью для удаление слов"""

    model = Word
    pk_url_kwarg = "pk_word"
    context_object_name = "word"
    # Нет шаблона подтверждения удаления,
    # подтверждение осуществляется через
    # всплывающее окно в браузере.
    template_name = None

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Удалено!")
        return response


class EditWordView(
    WordAcessMixin,
    NextUrlMixin,
    GetSuccessUrlMixin,
    UpdateView,
):
    """Редактирование слов"""

    model = Word
    template_name = "training/edit_word.html"
    form_class = EditWordForm
    pk_url_kwarg = "pk_word"

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Успешно!")
            return response
        except IntegrityError as e:
            messages.warning(self.request, f"Ошибка: {e}")
            return self.form_invalid(form)


class SearchView(BaseShowingViewMixin):
    """Вью для поиска"""

    page_title = "Результат поиска"
    empty_message = "Слов с таким ключевым словом не найдено"

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        if query:
            return Word.objects.filter(
                word__icontains=query,
                user=self.request.user,
            )
        return Word.objects.none()


class TrainingSetupView(LoginRequiredMixin, View):
    """Настройка и начало тренировки"""

    def get(self, request):
        """Показать форму настроек"""
        clean_session(request)

        Word.ensure_min_active_words(request.user)

        form = TrainingSettingsForm(user=request.user)
        return render(request, "training/train_setup.html", {"form": form})

    def post(self, request):
        """Обрабатывает настройки тренировки."""
        form = TrainingSettingsForm(request.POST, user=request.user)

        if not form.is_valid():
            return render(request, "training/train_setup.html", {"form": form})

        word_type = form.cleaned_data.get("word_type")
        count = form.cleaned_data.get("count")

        # Сохраняем настройки в сессию
        settings: dict = {
            "word_type": word_type,
            "count": count,
        }
        request.session.setdefault("training_settings", settings)

        # Формируем список слов
        word_ids = self._get_word_ids(request.user, form.cleaned_data)

        if not word_ids:
            messages.warning(
                request, "Нет слов для тренировки с выбранными параметрами!"
            )
            return redirect("training_setup")

        # Сохраняем ID слов в сессию (перемешанные)
        shuffle(word_ids)
        request.session.setdefault("training_words", word_ids)
        request.session.setdefault("training_current_index", 0)
        request.session.setdefault("training_session_id", None)

        # Переходим к первому слову
        return redirect("train_card")

    def _get_word_ids(self, user, cleaned_data) -> list[int]:
        """Формирует список ID слов по настройкам"""

        queryset = Word.words

        only_en_words = cleaned_data.get("only_en_words")
        only_ru_words = cleaned_data.get("only_ru_words")
        word_type = cleaned_data.get("word_type")

        # Фильтр по типу слов
        if word_type == "all":
            queryset = queryset.is_active(user).order_by("updated_at")
        elif word_type == "learned":
            queryset = queryset.is_learned(user).order_by("updated_at")
        elif word_type == "random":
            queryset = queryset.random_words(user)
        if only_en_words:
            queryset = queryset.filter(language="en")
        elif only_ru_words:
            queryset = queryset.filter(language="ru")

        # Ограничиваем количество
        return list(queryset.values_list("id", flat=True)[: cleaned_data["count"]])


class TrainCardView(LoginRequiredMixin, View):
    """Показывает текущее слово тренировки"""

    def get(self, request):
        """Показать карточку текущего слова"""

        training_words = request.session.get("training_words")
        current_index = request.session.get("training_current_index")

        word_id = training_words[current_index]
        word = Word.objects.get(id=word_id, user=request.user)

        # Прогресс
        progress: dict = {
            "current": current_index + 1,
            "total": len(training_words),
            "percent": (current_index + 1) / len(training_words) * 100,
        }

        context: dict = {
            "word": word,
            "progress": progress,
            "word_type": request.session["training_settings"]["word_type"],
        }

        return render(request, "training/train_card.html", context)


class TrainAnswerView(LoginRequiredMixin, View):
    """Обработка ответа пользователя"""

    def post(self, request):
        word_id = request.POST.get("word_id")
        is_known: bool = request.POST.get("is_known") == "true"
        is_abort: bool = request.POST.get("is_abort") == "true"

        if is_abort:
            return redirect("train_complete")

        word = Word.objects.get(id=word_id, user=request.user)

        # Меняем поле is_active на False уже тут
        word.update_review_schedule(is_known)

        # Создаём сессию тренировки, если ещё нет
        if not request.session["training_session_id"]:
            session = TrainingSession.objects.create(user=request.user)
            request.session["training_session_id"] = session.id
            request.session.setdefault("training_correct_count", 0)
            request.session.setdefault("training_incorrect_count", 0)
            request.session.setdefault("training_total_words", 0)

        session_id = request.session.get("training_session_id")
        session = TrainingSession.objects.get(id=session_id, user=request.user)

        # Обновляем статистику в сессии
        if is_known:
            request.session["training_correct_count"] = (
                request.session["training_correct_count"] + 1
            )
        else:
            request.session["training_incorrect_count"] = (
                request.session["training_incorrect_count"] + 1
            )

        request.session["training_total_words"] = (
            request.session["training_total_words"] + 1
        )

        # Переходим к следующему слову
        current_index = request.session.get("training_current_index", 0)
        request.session["training_current_index"] = current_index + 1

        training_words = request.session.get("training_words", [])

        if current_index + 1 >= len(training_words):
            return redirect("train_complete")

        return redirect("train_card")


class TrainCompleteView(LoginRequiredMixin, View):
    """Завершение тренировки — вывод статистики"""

    def get(self, request):
        """
        Обрабатывает GET-запрос для отображения
        результатов завершённой тренировки.

        Выполняет следующие действия:
            1. Восполняет активные слова до минимального
            количества (ensure_min_active_words).
            2. Проверяет, что тренировка действительно
            завершена (все слова отвечены).
            3. Извлекает статистику из сессии
            (количество правильных/неправильных ответов).
            4. Сохраняет сессию тренировки в базу данных
            (модель TrainingSession).
            5. Очищает временные данные тренировки из сессии.
            6. Рассчитывает процент правильных ответов.
            7. Рендерит страницу с итоговой статистикой.

        Args:
            request (HttpRequest): Объект HTTP-запроса,
            содержащий данные сессии.

        Returns:
            HttpResponse:
                - Редирект на страницу тренировки (train_card),
                если тренировка не завершена.
                - Рендер шаблона 'training/train_complete.html'
                с контекстом статистики.

        Context для шаблона:
            total_words (int): Общее количество отвеченных слов.
            correct_count (int): Количество правильных ответов.
            incorrect_count (int): Количество неправильных ответов.
            accuracy (float): Процент правильных ответов (округлён до 1 знака).
            word_type (str): Тип слов из настроек тренировки.
            session (TrainingSession | None): Объект сессии тренировки
            из БД (или None).

        Notes:
            - Перед рендером происходит восполнение
            активных слов до MIN_ACTIVE_WORDS.
            - Если сессия не была сохранена в БД (например, при прерывании),
            training_session будет None.
            - Данные тренировки извлекаются из сессии
            браузера и после сохранения
            полностью очищаются.
        """

        Word.ensure_min_active_words(request.user)

        settings = request.session.get("training_settings")

        # Получаем статистику из сессии
        total_words = request.session.get("training_total_words", 0)
        correct_count = request.session.get("training_correct_count", 0)
        incorrect_count = request.session.get("training_incorrect_count", 0)

        # Создаём сессию в БД (если ещё не создана)
        session_id = request.session.get("training_session_id")
        if session_id:
            training_session = TrainingSession.objects.get(
                id=session_id, user=request.user
            )
            training_session.ended_at = timezone.now()
            training_session.total_words = total_words
            training_session.correct_words = correct_count
            training_session.incorrect_words = incorrect_count
            training_session.save()
        else:
            return redirect("training_setup")

        clean_session(request)
        # Рассчитываем процент правильных ответов
        accuracy = 0
        if total_words > 0:
            accuracy = round(correct_count / total_words * 100, 1)

        context = {
            "total_words": total_words,
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "accuracy": accuracy,
            "word_type": settings["word_type"],
            "session": training_session,
        }

        return render(request, "training/train_complete.html", context)


class ResetLearnedWordsView(LoginRequiredMixin, View):
    """
    Вью для сброса выученных
    слов (переводит флаг is learned
    на False для всех слов пользователя).
    """

    def post(self, request):
        """
        Перевод флага is_learned
        на False для сброса слов.
        """
        Word.words.is_learned(request.user).update(
            is_learned=False,
            next_review_date=timezone.now(),
        )
        return redirect("word_manager")


class WordManagerView(LoginRequiredMixin, TemplateView):
    """Вью для менеджера  слов"""

    template_name = "users/word_manager.html"
