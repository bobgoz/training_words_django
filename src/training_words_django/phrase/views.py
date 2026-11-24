import csv
import io
import logging

from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
)
from training.forms import CSVUploadForm
from training.mixins import LoginRequiredMixin

from .forms import CreatePhraseForm, EditPhraseForm
from .mixins import BaseShowingViewMixin
from .models import Phrase

logger = logging.getLogger(__name__)


class PhraseCreateView(LoginRequiredMixin, CreateView):
    """Вью для создания словосочетания"""

    model = Phrase
    template_name = 'phrase/create_phrase.html'
    form_class = CreatePhraseForm
    success_url = reverse_lazy('add_phrase')

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Словосочетание добавлено!')
            return response
        except IntegrityError:
            phrase = form.cleaned_data['phrase']
            messages.warning(
                self.request,
                f'Словосочетание {phrase} уже существует!',
            )
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['file_form'] = CSVUploadForm()
        return context


class DetailPhraseView(
    LoginRequiredMixin,
    DetailView,
):
    """Вью  для детального отображения."""

    model = Phrase
    template_name = 'phrase/detail.html'
    pk_url_kwarg = 'pk_phrase'


class EditPhraseView(LoginRequiredMixin, UpdateView):
    """Вью для редактирования объектов."""

    model = Phrase
    template_name = 'phrase/edit.html'
    form_class = EditPhraseForm
    pk_url_kwarg = 'pk_phrase'


class DeletePhraseView(LoginRequiredMixin, DeleteView):
    """Вью для удаления объектов."""

    model = Phrase
    pk_url_kwarg = 'pk_phrase'
    context_object_name = 'phrase'
    template_name = None
    success_url = reverse_lazy('active_phrases')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Удалено!')
        return response


class ShowActivePhrasesView(BaseShowingViewMixin):
    """Вью для отображения актианых словосочетаний."""

    page_title = 'Активные словосочетания (участвуют в тренировке)'
    empty_message = 'Нет активныз словосочетаний'

    def get_queryset(self):
        return Phrase.phrases.is_active(self.request.user)


class ShowInactivePhrasesView(BaseShowingViewMixin):
    """Вью для отображения новых (неактивных) словосочетаний"""

    page_title = 'Новые словосочетания, в ожидании изучения'
    empty_message = 'Нет новых словосочетаний'

    def get_queryset(self):
        return Phrase.phrases.inactive(self.request.user)


class ShowLearnedPhrasesView(BaseShowingViewMixin):
    """Вью для отображения изученных словосочетаний"""

    page_title = 'Выученные словосочетания'
    empty_message = 'Нет выученных словосочетаний'

    def get_queryset(self):
        return Phrase.phrases.is_learned(self.request.user)


class CSVDownloadPhrasesView(View):
    """Вью для обработки загрузки csv-файла с данными."""

    def post(self, request):
        """Обработка post-запроса."""

        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data.get('file')
            text_stream = io.TextIOWrapper(
                uploaded_file.file,
                encoding='utf-8',
                newline='',
            )
            csv_reader = csv.DictReader(text_stream)
            try:
                for row in csv_reader:
                    phrase = row['phrase']
                    if not Phrase.objects.filter(
                        phrase=phrase, user=request.user
                    ).exists():
                        Phrase.objects.create(phrase=phrase, user=request.user)
                messages.success(
                    request,
                    'Успешно загружены словосочетания в словарь из файла.',
                )
            except KeyError as e:
                messages.warning(
                    request,
                    'В загруженном файле не найдено ключевое слово "phrase".',
                )
                logger.warning(e)

            except Exception as e:
                messages.warning(
                    request,
                    'Произошла ошибка на стороне сервера.',
                )
                logger.warning(e)
                raise

        return redirect('add_word')
