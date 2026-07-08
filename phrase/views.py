from django.contrib import messages
from django.db import IntegrityError
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from training.mixins import LoginRequiredMixin

from .forms import CreatePhraseForm
from .models import Phrase


class PhraseCreateView(LoginRequiredMixin, CreateView):
    """Вью для создания словосочетания"""

    model = Phrase
    template_name = "training/create_phrase.html"
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


class PhraseManagerView(LoginRequiredMixin, TemplateView):
    """Вью для менеджера словосочетаний."""

    template_name = "users/"
