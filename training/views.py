from random import shuffle

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
)

from .forms import CreateWordForm, EditWordForm
from .mixins import (
    BaseTrainingViewMixin,
    WordAcessMixin,
    NextUrlMixin,
    GetSuccessUrlMixin,
)
from .models import Word

from .constants import COUNT_RANDOM_WORDS, COUNT_WORDS_FOR_ACTIVATE


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


class TrainingLearnedView(BaseTrainingViewMixin):
    """Вью для отображения только изученных слов"""

    def get_queryset(self):
        """Возвращает список изученных слов"""
        return Word.words.is_learned(self.request.users)


class TrainingNoActiveView(BaseTrainingViewMixin):
    """Вью для отображения неактивных слов"""

    def get_queryset(self):
        """Возвращает список неактивных слов"""
        return Word.words.is_not_active(self.request.user).order_by('-created_at')


class TrainingHardView(BaseTrainingViewMixin):
    """Вью для отображения сложных слов"""

    def get_queryset(self):
        """Возвращает список сложных слов"""
        return Word.words.is_hard(self.request.user)


class TrainingRandomView(BaseTrainingViewMixin):
    """Вью для отображения случайных слов"""

    # Отключение пагинации
    paginate_by = None

    def get_queryset(self):
        """Возвращает срез рандомных слов"""
        return Word.words.random_words(self.request.user)[:COUNT_RANDOM_WORDS]


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
        print(query)

        if query:
            return Word.objects.filter(
                word__icontains=query,
                user=self.request.user,
            )
        return Word.objects.none()
