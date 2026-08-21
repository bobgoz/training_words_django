from django.contrib import messages
from django.db import IntegrityError
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    TemplateView,
    UpdateView,
)

from training.mixins import LoginRequiredMixin

from .forms import CreatePhraseForm, EditPhraseForm
from .mixins import BaseShowingViewMixin
from .models import Phrase


class PhraseCreateView(LoginRequiredMixin, CreateView):
    """Вью для создания словосочетания"""

    model = Phrase
    template_name = "phrase/create_phrase.html"
    form_class = CreatePhraseForm
    success_url = reverse_lazy("add_phrase")

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Словосочетание добавлено!")
            return response
        except IntegrityError:
            phrase = form.cleaned_data["phrase"]
            messages.warning(
                self.request,
                f"Словосочетание {phrase} уже существует!",
            )
            return self.form_invalid(form)


class DetailPhraseView(
    LoginRequiredMixin,
    DetailView,
):
    """Вью  для детального отображения."""

    model = Phrase
    template_name = "phrase/detail.html"
    pk_url_kwarg = "pk_phrase"


class EditPhraseView(LoginRequiredMixin, UpdateView):
    """Вью для редактирования объектов."""

    model = Phrase
    template_name = "phrase/edit.html"
    form_class = EditPhraseForm
    pk_url_kwarg = "pk_phrase"


class DeletePhraseView(LoginRequiredMixin, DeleteView):
    """Вью для удаления объектов."""

    model = Phrase
    pk_url_kwarg = "pk_phrase"
    context_object_name = "phrase"
    template_name = None
    success_url = reverse_lazy("phrase_manager")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Удалено!")
        return response


class PhraseManagerView(LoginRequiredMixin, TemplateView):
    """Вью для менеджера словосочетаний."""

    template_name = "users/phrase_manager.html"


class ShowActivePhrasesView(BaseShowingViewMixin):
    """Вью для отображения актианых словосочетаний."""

    page_title = "Активные словосочетания (участвуют в тренировке)"
    empty_message = "Нет активныз словосочетаний"

    def get_queryset(self):
        return Phrase.phrases.is_active(self.request.user)


class ShowInactivePhrasesView(BaseShowingViewMixin):
    """Вью для отображения новых (неактивных) словосочетаний"""

    page_title = "Новые словосочетания, в ожидании изучения"
    empty_message = "Нет новых словосочетаний"

    def get_queryset(self):
        return Phrase.phrases.inactive(self.request.user)


class ShowLearnedPhrasesView(BaseShowingViewMixin):
    """Вью для отображения изученных словосочетаний"""

    page_title = "Выученные словосочетания"
    empty_message = "Нет выученных словосочетаний"

    def get_queryset(self):
        return Phrase.phrases.is_learned(self.request.user)
