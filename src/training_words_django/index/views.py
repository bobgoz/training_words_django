from django.views.generic import TemplateView

from training_words_django.phrase.models import Phrase
from training_words_django.training.models import Word


class IndexView(TemplateView):
    """Вью для управления главной страницей"""

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        """Передача в контекст количества"""
        context = super().get_context_data(**kwargs)

        user = self.request.user

        if user.is_authenticated:
            # Слова.
            context["learned_words"] = Word.words.count_all_learned(
                user,
            )
            context["total_words"] = Word.words.count_all_words(
                user,
            )
            context["active_words"] = Word.words.count_active(
                user,
            )
            context["count_inactive"] = Word.words.count_inactive(
                user,
            )
            # Словосочетания.
            context["total_phrases"] = Phrase.phrases.count_all_phrases(
                user,
            )
            context["inactive_phrases"] = Phrase.phrases.count_inactive(
                user,
            )
            context["active_phrases"] = Phrase.phrases.count_active(
                user,
            )
            context["learned_phrases"] = Phrase.phrases.count_all_learned(
                user,
            )

        return context
