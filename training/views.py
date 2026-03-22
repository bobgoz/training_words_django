from django.shortcuts import render
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
)
from random import shuffle
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render

from .forms import CreateWordForm, EditWordForm
from .models import Word
from django.shortcuts import redirect


class WordCreateView(LoginRequiredMixin, CreateView):
    """Вью для создания слов"""

    model = Word
    template_name = 'training/create_word.html'
    form_class = CreateWordForm
    success_url = reverse_lazy('add_word')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.word = form.instance.word.capitalize()
        form.instance.word = form.instance.word.strip()
        form.instance.definition = form.instance.definition.capitalize()
        return super().form_valid(form)


class TrainingView(LoginRequiredMixin, ListView):
    """Вью для тренировки (отображения слов)"""

    template_name = 'training/training.html'
    context_object_name = 'words'
    paginate_by = 10

    def get_queryset(self):
        return Word.objects.filter(
            user=self.request.user,
            is_active=True,
        )


class DetailWordView(LoginRequiredMixin, DetailView):
    """Вью для детального отображения и редактирования слов"""

    template_name = 'training/detail_word.html'
    success_url = reverse_lazy('training')
    pk_url_kwarg = 'pk_word'

    def get_queryset(self):
        return Word.objects.filter(user=self.request.user)


class DeleteWordView(LoginRequiredMixin, DeleteView):
    """Вью для удаление слов"""

    model = Word
    pk_url_kwarg = 'pk_word'
    context_object_name = 'word'
    success_url = reverse_lazy('training')


class ConfirmDeleteWordView(LoginRequiredMixin, DetailView):
    """Подтверждение перед удалением слова"""

    model = Word
    template_name = 'training/confirmation_delete_word.html'
    context_object_name = 'word'
    pk_url_kwarg = 'pk_word'


class WordsView(LoginRequiredMixin, ListView):
    """Отображение списка слов"""

    queryset = Word.objects.all().order_by('pk')
    template_name = 'training/words.html'
    context_object_name = 'words'


class MarkAsActiveView(LoginRequiredMixin, View):
    """Помечает 10 слов как активные"""

    def post(self, request, *args, **kwargs):
        words_idx = list(
            Word.objects.filter(
                user=self.request.user,
                is_active=False,
            )
            .order_by('pk')
            .values_list('pk', flat=True)[:10]
        )
        Word.objects.filter(id__in=words_idx).update(is_active=True)

        return redirect('training')


class EditWordView(UpdateView):
    """Редактирование слов"""

    model = Word
    template_name = 'training/edit_word.html'
    form_class = EditWordForm
    success_url = reverse_lazy('training')
    pk_url_kwarg = 'pk_word'


class ShowRandomView(LoginRequiredMixin, View):
    """Рандомизирует слова"""

    def get(self, request, *args, **kwargs):
        random_words = Word.objects.filter(
            user=self.request.user,
            is_active=True,
        ).order_by('?')[:10]

        return render(
            request,
            template_name='training/training.html',
            context={'random_words': random_words},
        )
