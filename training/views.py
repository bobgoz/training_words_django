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
from .mixins import BaseTrainingViewMixin, WordAcessMixin
from .models import Word

from .constants import COUNT_RANDOM_WORDS


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
    """Вью для тренировки (отображения слов)"""

    def get_queryset(self):
        """Возвращает список активных слов"""
        return Word.words.is_active(self.request.user)


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


class TrainingRandomView(BaseTrainingViewMixin):
    """Вью для отображения случайных слов"""

    # Отключение пагинации
    paginate_by = None

    def get_queryset(self):
        """Возвращает срез рандомных слов"""
        return Word.words.random_words(self.request.user)[:COUNT_RANDOM_WORDS]


class DetailWordView(LoginRequiredMixin, WordAcessMixin, DetailView):
    """Вью для детального отображения"""

    model = Word
    template_name = 'training/detail_word.html'
    success_url = reverse_lazy('training')
    pk_url_kwarg = 'pk_word'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next')
        return context


class DeleteWordView(LoginRequiredMixin, WordAcessMixin, DeleteView):
    """Вью для удаление слов"""

    model = Word
    pk_url_kwarg = 'pk_word'
    context_object_name = 'word'
    # success_url = reverse_lazy('training')

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('training')



class MarkAsActiveView(LoginRequiredMixin, View):
    """Помечает 10 слов как активные"""

    def post(self, request, *args, **kwargs):
        words_idx = list(
            Word.words.is_not_active(
                self.request.user,
            ).values_list(
                'pk', flat=True
            )[:10],
        )
        Word.words.filter(id__in=words_idx).update(is_active=True)
        return redirect('training')


class EditWordView(WordAcessMixin, UpdateView):
    """Редактирование слов"""

    model = Word
    template_name = 'training/edit_word.html'
    form_class = EditWordForm
    pk_url_kwarg = 'pk_word'

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('detail', kwargs={'pk_word': self.object.pk})
