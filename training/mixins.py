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


class BaseTrainingViewMixin(LoginRequiredMixin, ListView):
    """Общий класс для всех тренировок"""

    template_name = 'training/training.html'
    context_object_name = 'words'
    paginate_by: int | None = 10
