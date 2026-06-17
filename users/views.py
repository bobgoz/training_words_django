from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    TemplateView,
    UpdateView,
)

from training.models import TrainingSession, Word

from .forms import RegisterForm, SimplePasswordForm

User = get_user_model()


class RegistrationView(CreateView):
    """Вью для регистрации"""

    template_name = 'registration/registration.html'
    form_class = RegisterForm
    success_url = '/login'


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile_base.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.request.user


class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = 'users/profile_edit.html'
    fields = (
        'username',
        'first_name',
        'last_name',
        'email',
        'avatar',
        'bio',
    )

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('profile')


class ProfileInfoView(LoginRequiredMixin, DetailView):
    """Информация о профиле"""

    model = User
    template_name = 'users/profile_info.html'

    def get_object(self):
        return self.request.user


class SimplePasswordChangeView(LoginRequiredMixin, FormView):
    """Вью  для переназначения пароля в профиле."""

    template_name = 'registration/simple_password_change.html'
    form_class = SimplePasswordForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        user = self.request.user
        new_password = form.cleaned_data['new_password1']
        user.set_password(new_password)
        user.save()

        messages.success(self.request, 'Пароль успешно изменён!')
        return super().form_valid(form)


class StatisticsView(LoginRequiredMixin, TemplateView):
    """Вью для отображения статистики пользователя"""

    template_name = 'stats/statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()
        month_ago = now - timedelta(days=30)

        # Базовые данные
        all_words = Word.objects.filter(user=user)
        active_words = Word.words.is_active(user)
        inactive_words = Word.words.is_not_active(user)
        learned_words = Word.words.is_learned(user)
        hard_words = Word.words.is_hard(user)

        total_count = all_words.count()
        active_count = active_words.count()
        inactive_count = inactive_words.count()
        learned_count = learned_words.count()
        hard_count = hard_words.count()

        # Эффективность
        # Формула: (активные слова / все слова) * 100%
        # Чем больше активных слов, тем больше пользователь тренируется
        efficiency = 0
        if total_count > 0:
            efficiency = round(active_count / total_count * 100, 1)

        # Прогресс изучения
        # Формула: (изученные слова / все слова) * 100%
        learning_progress = 0
        if total_count > 0:
            learning_progress = round(learned_count / total_count * 100, 1)

        # Слова за последний месяц
        words_added_month = all_words.filter(created_at__gte=month_ago).count()
        words_learned_month = learned_words.filter(
            updated_at__gte=month_ago
        ).count()

        # Активность (тренировки за последние 30 дней)
        sessions = TrainingSession.objects.filter(
            user=user, started_at__gte=month_ago
        )
        sessions_count = sessions.count()
        total_trainings = (
            sessions.aggregate(total=models.Sum('total_words'))['total'] or 0
        )
        correct_trainings = (
            sessions.aggregate(total=models.Sum('correct_words'))['total'] or 0
        )

        avg_accuracy = 0
        if total_trainings > 0:
            avg_accuracy = round(correct_trainings / total_trainings * 100, 1)

        context.update(
            {
                # Статистика слов
                'total_count': total_count,
                'active_count': active_count,
                'inactive_count': inactive_count,
                'learned_count': learned_count,
                'hard_count': hard_count,
                'efficiency': efficiency,
                'learning_progress': learning_progress,
                # Динамика за месяц
                'words_added_month': words_added_month,
                'words_learned_month': words_learned_month,
                # Активность тренировок
                'sessions_count': sessions_count,
                'total_trainings': total_trainings,
                'correct_trainings': correct_trainings,
                'avg_accuracy': avg_accuracy,
            }
        )

        return context
