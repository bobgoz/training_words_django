from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy
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
        return context


class NextUrlMixin:
    """Миксин, содержащий логику передачи в сессию ссылки с пагинацией"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем next из GET параметров
        next_url = self.request.GET.get('next')

        # Получаем referer (откуда пришли)
        referer = self.request.META.get('HTTP_REFERER')

        if next_url:
            # Если есть next — сохраняем его
            self.request.session['saved_next'] = next_url
            context['next'] = next_url
        elif referer and 'words' in referer:
            # Если пришли со страницы списка слов — сохраняем referer
            self.request.session['saved_next'] = referer
            context['next'] = referer
        else:
            # Иначе используем сохранённый
            context['next'] = self.request.session.get('saved_next')

        return context


class GetSuccessUrlMixin:
    """
    Миксин для вьюх, где требуется
    корректный переход в список слов
    с пагинацией.
    """

    def get_success_url(self):
        """
        Получение ссылки с пагинацией
        из сессии и переход по ней.
        """
        next_url = self.request.session.get('saved_next', None)

        # Если есть сохранённый URL — удаляем его из сессии (чтобы не залипал)
        if next_url:
            self.request.session.pop('saved_next', None)
            return next_url

        # Если нет — перенаправляем на менеджер слов
        return reverse_lazy('word_manager')
