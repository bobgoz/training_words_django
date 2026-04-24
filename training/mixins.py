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


class BaseTrainingViewMixin(LoginRequiredMixin, ListView):
    """Общий класс для всех тренировок"""

    template_name = 'training/training.html'
    context_object_name = 'words'
    paginate_by: int | None = 10


class NextUrlMixin:
    """Миксин, содержащий логику передачи в сессию ссылки с пагинацией"""

    def get_context_data(self, **kwargs):
        """
        Передача в сессию url-а, который может
        содержать в себе номер пагинации,
        предназначен для возврата в список
        слов с последней пагинацией.
        """
        context = super().get_context_data(**kwargs)
        next_url = self.request.GET.get('next')
        if next_url:
            self.request.session['saved_next'] = next_url
        else:
            next_url = self.request.session.get('saved_next')
        context['next'] = next_url
        return context


class GetSuccessUrlMixin:
    """
    Миксин для вьюх, где требуется
    корректный переход в список слов
    с пагинацмей.
    """

    def get_success_url(self):
        """
        Получение ссылки с пагинацией
        из сессии и переход по ней.
        """
        next_url = self.request.session.get('saved_next', None)
        return next_url or reverse_lazy('training')
