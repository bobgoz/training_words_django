from random import shuffle

from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CreateWordForm, EditWordForm
from .models import Word

COUNT_RANDOM_WORDS = 10


class WordAcessMixin(AccessMixin):
    """
    Проверка доступа к слову.
    Если объект не принадлежит пользователю, возвращается ошибка 404.
    """

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != request.user:
            raise Http404('Запрашиваемого слова не существует.')
        return super().dispatch(request, *args, **kwargs)


class WordCreateView(LoginRequiredMixin, CreateView):
    """Вью для создания слов"""

    model = Word
    template_name = 'training/create_word.html'
    form_class = CreateWordForm
    success_url = reverse_lazy('add_word')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TrainingView(LoginRequiredMixin, ListView):
    """Вью для тренировки (отображения слов)"""

    template_name = 'training/training.html'
    context_object_name = 'words'
    paginate_by = 10

    def get_queryset(self):
        """
        Определяет вывод списка слов
        в зависимости от режима.
        """

        user = self.request.user
        words = Word.words
        action = self.request.GET.get('action')

        if action == 'hard':
            return words.hard(user)
        if action == 'random':
            return words.random_words(user, COUNT_RANDOM_WORDS)
        return words.active(user)


class DetailWordView(LoginRequiredMixin, WordAcessMixin, DetailView):
    """Вью для детального отображения и редактирования слов"""

    model = Word
    template_name = 'training/detail_word.html'
    success_url = reverse_lazy('training')
    pk_url_kwarg = 'pk_word'


class DeleteWordView(LoginRequiredMixin, WordAcessMixin, DeleteView):
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
        Word.words.filter(id__in=words_idx).update(is_active=True)
        print(words_idx)

        return redirect('training')


class EditWordView(WordAcessMixin, UpdateView):
    """Редактирование слов"""

    model = Word
    template_name = 'training/edit_word.html'
    form_class = EditWordForm
    success_url = reverse_lazy('training')
    pk_url_kwarg = 'pk_word'
