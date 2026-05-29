from random import shuffle
from django.utils import timezone


from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
)

from .constants import COUNT_WORDS_FOR_ACTIVATE
from .forms import CreateWordForm, EditWordForm, TrainingSettingsForm
from .mixins import (
    BaseTrainingViewMixin,
    GetSuccessUrlMixin,
    NextUrlMixin,
    WordAcessMixin,
)
from .models import TrainingSession, Word, WordAttempt


class WordCreateView(LoginRequiredMixin, CreateView):
    """Вью для создания слов"""

    model = Word
    template_name = 'training/create_word.html'
    form_class = CreateWordForm
    success_url = reverse_lazy('add_word')

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            return super().form_valid(form)
        except IntegrityError:
            form.add_error('word', 'Такое слово уже есть в словаре!')
            return self.form_invalid(form)


class TrainingView(BaseTrainingViewMixin):
    """Вью для тренировки (отображения активных слов)"""

    def get_queryset(self):
        """Возвращает список активных слов"""
        user = self.request.user

        if self._has_english_words:
            lang = self.request.GET.get('lang', 'all')
            if lang == 'ru':
                return Word.words.language_ru(user)
            elif lang == 'en':
                return Word.words.language_en(user)

        return Word.words.is_active(user)

    def get_context_data(self, **kwargs):
        """Передача флага has_en_words в контекст."""
        context = super().get_context_data(**kwargs)
        context['has_en_words'] = self._has_english_words
        return context

    @property
    def _has_english_words(self) -> bool:
        """
        Возвращает True, если в списке
        слов пользователя есть слова других
        языков.
        """
        return Word.words.language_en(self.request.user).exists()


class TrainingNoActiveView(BaseTrainingViewMixin):
    """Вью для отображения неактивных слов"""

    def get_queryset(self):
        """Возвращает список неактивных слов"""
        return Word.words.is_not_active(self.request.user)


class TrainingHardView(BaseTrainingViewMixin):
    """Вью для отображения сложных слов"""

    def get_queryset(self):
        """Возвращает список сложных слов"""
        return Word.words.is_hard(self.request.user)


class ShowLearnedView(BaseTrainingViewMixin):
    """Вью для просмотра выученных слов."""

    def get_queryset(self):
        """Возвращает список выученных слов"""
        return Word.words.is_learned(self.request.user)


class DetailWordView(
    LoginRequiredMixin,
    WordAcessMixin,
    NextUrlMixin,
    DetailView,
):
    """Вью для детального отображения"""

    model = Word
    template_name = 'training/detail_word.html'
    pk_url_kwarg = 'pk_word'


class DeleteWordView(
    LoginRequiredMixin,
    WordAcessMixin,
    GetSuccessUrlMixin,
    DeleteView,
):
    """Вью для удаление слов"""

    model = Word
    pk_url_kwarg = 'pk_word'
    context_object_name = 'word'
    # Нет шаблона подтверждения удаления,
    # подтверждение осуществляется через
    # всплывающее окно в браузере.
    template_name = None


class MarkAsActiveView(LoginRequiredMixin, View):
    """Помечает 10 слов как активные"""

    def post(self, request, *args, **kwargs):
        words_idx = list(
            Word.words.is_not_active(
                self.request.user,
            )
            .values_list('pk', flat=True)
            .order_by('-updated_at')[:COUNT_WORDS_FOR_ACTIVATE],
        )
        Word.words.filter(id__in=words_idx).update(is_active=True)
        return redirect('training')


class DeactivateWordView(LoginRequiredMixin, View):
    """Деактивирует 10 первых слов."""

    def post(self, request, *args, **kwargs):
        words_ids = list(
            Word.words.is_active(
                request.user,
            )
            .order_by('-updated_at')
            .values_list('pk', flat=True)[:COUNT_WORDS_FOR_ACTIVATE]
        )
        Word.words.filter(pk__in=words_ids).update(is_active=False)

        return redirect('training')


class EditWordView(
    WordAcessMixin,
    NextUrlMixin,
    GetSuccessUrlMixin,
    UpdateView,
):
    """Редактирование слов"""

    model = Word
    template_name = 'training/edit_word.html'
    form_class = EditWordForm
    pk_url_kwarg = 'pk_word'


class MakeAsLearnedView(LoginRequiredMixin, View):
    """Помечает слово как изученное"""

    def post(self, request, *args, **kwargs):
        word_id = request.POST.get('word_id')
        next_url = request.POST.get('next', reverse_lazy('training'))
        word = Word.objects.get(pk=word_id, user=request.user)
        word.is_learned = True
        word.save()

        return redirect(next_url)


class SearchView(BaseTrainingViewMixin):
    """Вью для поиска"""

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
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

        Word.words.ensure_min_active_words(request.user)

        form = TrainingSettingsForm()
        return render(request, 'training/train_setup.html', {'form': form})

    def post(self, request):
        """Обрабатывает настройки тренировки."""
        form = TrainingSettingsForm(request.POST)

        if not form.is_valid():
            return render(request, 'training/train_setup.html', {'form': form})

        # Сохраняем настройки в сессию
        settings: dict = {
            'word_type': form.cleaned_data['word_type'],
            'count': form.cleaned_data['count'],
        }
        request.session.setdefault('training_settings', settings)

        # Формируем список слов
        word_ids = self._get_word_ids(request.user, form.cleaned_data)

        if not word_ids:
            messages.warning(
                request, 'Нет слов для тренировки с выбранными параметрами!'
            )
            return redirect('training_setup')

        # Сохраняем ID слов в сессию (перемешанные)
        shuffle(word_ids)
        request.session.setdefault('training_words', word_ids)
        request.session.setdefault('training_current_index', 0)
        request.session.setdefault('training_session_id', None)

        # Переходим к первому слову
        return redirect('train_card')

    def _get_word_ids(self, user, cleaned_data) -> list[int]:
        """Формирует список ID слов по настройкам"""

        queryset = Word.words

        # Фильтр по типу слов
        if cleaned_data['word_type'] == 'all':
            queryset = queryset.is_active(user).order_by('updated_at')
        elif cleaned_data['word_type'] == 'hard':
            queryset = queryset.is_hard(user).order_by('updated_at')
        elif cleaned_data['word_type'] == 'learned':
            queryset = queryset.is_learned(user).order_by('updated_at')
        elif cleaned_data['word_type'] == 'random':
            queryset = queryset.random_words(user)

        # Ограничиваем количество
        word_ids = list(
            queryset.values_list('id', flat=True)[: cleaned_data['count']]
        )

        return word_ids


class TrainCardView(LoginRequiredMixin, View):
    """Показывает текущее слово тренировки"""

    def get(self, request):
        """Показать карточку текущего слова"""

        training_words = request.session['training_words']
        current_index = request.session['training_current_index']

        word_id = training_words[current_index]
        word = Word.objects.get(id=word_id, user=request.user)

        # Прогресс
        progress: dict = {
            'current': current_index + 1,
            'total': len(training_words),
            'percent': (current_index + 1) / len(training_words) * 100,
        }

        context: dict = {
            'word': word,
            'progress': progress,
            'word_type': request.session['training_settings']['word_type'],
        }

        return render(request, 'training/train_card.html', context)


class TrainAnswerView(LoginRequiredMixin, View):
    """Обработка ответа пользователя"""

    def post(self, request):
        word_id = request.POST.get('word_id')
        is_known: bool = request.POST.get('is_known') == 'true'
        is_abort: bool = request.POST.get('is_abort') == 'true'

        if is_abort:
            return redirect('train_complete')

        word = Word.objects.get(id=word_id, user=request.user)

        # Меняем поле is_active на False уже тут
        word.update_review_schedule(is_known)

        # Создаём сессию тренировки, если ещё нет
        if not request.session['training_session_id']:
            session = TrainingSession.objects.create(user=request.user)
            request.session['training_session_id'] = session.id
            request.session.setdefault('training_correct_count', 0)
            request.session.setdefault('training_incorrect_count', 0)
            request.session.setdefault('training_total_words', 0)

        session_id = request.session.get('training_session_id')
        session = TrainingSession.objects.get(id=session_id, user=request.user)

        # Сохраняем ответ пользователя.
        WordAttempt.objects.create(
            user=request.user, word=word, session=session, is_correct=is_known
        )

        # Обновляем статистику в сессии
        if is_known:
            request.session['training_correct_count'] = (
                request.session['training_correct_count'] + 1
            )
        else:
            request.session['training_incorrect_count'] = (
                request.session['training_incorrect_count'] + 1
            )

        request.session['training_total_words'] = (
            request.session['training_total_words'] + 1
        )

        # Переходим к следующему слову
        current_index = request.session.get('training_current_index', 0)
        request.session['training_current_index'] = current_index + 1

        training_words = request.session.get('training_words', [])

        if current_index + 1 >= len(training_words):
            return redirect('train_complete')

        return redirect('train_card')


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

        Word.words.ensure_min_active_words(request.user)

        settings = request.session['training_settings']

        # Получаем статистику из сессии
        total_words = request.session.get('training_total_words', 0)
        correct_count = request.session.get('training_correct_count', 0)
        incorrect_count = request.session.get('training_incorrect_count', 0)

        # Создаём сессию в БД (если ещё не создана)
        session_id = request.session['training_session_id']
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
            # Если сессия не была создана
            # (например, пользователь прервал тренировку)
            training_session = None

        # Очищаем сессию
        request.session.pop('training_words', None)
        request.session.pop('training_current_index', None)
        request.session.pop('training_settings', None)
        request.session.pop('training_session_id', None)
        request.session.pop('training_correct_count', None)
        request.session.pop('training_incorrect_count', None)
        request.session.pop('training_total_words', None)

        # Рассчитываем процент правильных ответов
        accuracy = 0
        if total_words > 0:
            accuracy = round(correct_count / total_words * 100, 1)

        context = {
            'total_words': total_words,
            'correct_count': correct_count,
            'incorrect_count': incorrect_count,
            'accuracy': accuracy,
            'word_type': settings['word_type'],
            'session': training_session,
        }

        return render(request, 'training/train_complete.html', context)


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
        )
        return redirect('profile')
