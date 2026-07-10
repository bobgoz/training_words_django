from django.views.generic import ListView

from training.mixins import LoginRequiredMixin


class BaseShowingViewMixin(LoginRequiredMixin, ListView):
    """Общий класс для всех вью для показа различных типов словосочетаний."""

    template_name = "phrase/list.html"
    context_object_name = "phrases"
    paginate_by: int | None = 10
    page_title = None
    empty_message = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.page_title is None:
            raise NotImplementedError(
                f"Класс {self.__class__.__name__} должен определить "
                "атрибут page_title при наследовании."
            )
        if self.empty_message is None:
            raise NotImplementedError(
                f"Класс {self.__class__.__name__} должен определить "
                "атрибут empty_message при наследовании."
            )
        context["page_title"] = self.page_title
        context["empty_message"] = self.empty_message
        return context
