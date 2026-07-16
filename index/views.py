from django.views.generic import TemplateView

from training.models import Word


class IndexView(TemplateView):
    """Вью для управления главной страницей"""

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        """Передача в контекст количества слов"""
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context["learned_words"] = Word.words.count_all_learned(
                self.request.user,
            )
            context["total_words"] = Word.words.count_all_words(
                self.request.user,
            )
            context["active_words"] = Word.words.count_active(
                self.request.user,
            )
            context["count_inactive"] = Word.words.count_inactive(
                self.request.user,
            )

        return context
