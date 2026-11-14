from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.http import Http404
from django.views.generic import ListView


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


class BaseShowingViewMixin(LoginRequiredMixin, ListView):
    """Общий класс для всех вью для показа различных типов слов."""

    template_name = 'training/word_list.html'
    context_object_name = 'words'
    paginate_by: int | None = 10
    page_title = None
    empty_message = None

    ordering_map = dict(
        alphabet='word', updated='-updated_at', repetition_count='-repetition_count'
    )
    default_order = 'alphabet'

    def apply_erdering(self, queryset):
        """Сортирует queryset по разрешённому параметру order."""
        order = self.request.GET.get('order', self.default_order)
        ordering = self.ordering_map.get(order, self.ordering_map[self.default_order])
        return queryset.order_by(ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.page_title is None:
            raise NotImplementedError(
                f'Класс {self.__class__.__name__} должен определить '
                'атрибут page_title при наследовании.'
            )
        if self.empty_message is None:
            raise NotImplementedError(
                f'Класс {self.__class__.__name__} должен определить '
                'атрибут empty_message при наследовании.'
            )
        context['page_title'] = self.page_title
        context['empty_message'] = self.empty_message
        context['current_order'] = self.request.GET.get(
            'order',
            self.default_order,
        )
        return context
