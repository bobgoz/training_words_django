from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.db import models
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    TemplateView,
    UpdateView,
)
from training.models import TrainingSession, Word

from .forms import RegisterForm, SimplePasswordForm
from .utils import send_verification_email

User = get_user_model()


class RegistrationView(CreateView):
    """Вью для регистрации"""

    template_name = "registration/registration.html"
    form_class = RegisterForm
    success_url = "/login"

    def form_valid(self, form):
        response = super().form_valid(form)
        request = self.request
        send_verification_email(
            request=request,
            user=self.object,
        )
        messages.info(
            request,
            "Аккаунт создан. Мы отправили ссылку для подтверждения почты — "
            "но пользоваться сайтом можно уже сейчас.",
        )

        return response


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "users/profile_base.html"
    context_object_name = "profile"

    def get_object(self):
        return self.request.user


class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = "users/profile_edit.html"
    fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "avatar",
        "bio",
    )

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy("profile")


class ProfileInfoView(LoginRequiredMixin, DetailView):
    """Информация о профиле"""

    model = User
    template_name = "users/profile_info.html"

    def get_object(self):
        return self.request.user


class SimplePasswordChangeView(LoginRequiredMixin, FormView):
    """Вью  для переназначения пароля в профиле."""

    template_name = "registration/simple_password_change.html"
    form_class = SimplePasswordForm
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        user = self.request.user
        new_password = form.cleaned_data["new_password1"]
        user.set_password(new_password)
        user.save()

        messages.success(self.request, "Пароль успешно изменён!")
        return super().form_valid(form)


class StatisticsView(LoginRequiredMixin, TemplateView):
    """Вью для отображения статистики пользователя"""

    template_name = "stats/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()
        month_ago = now - timedelta(days=30)

        # Базовые данные
        all_words = Word.objects.filter(user=user)
        active_words = Word.words.is_active(user)
        inactive_words = Word.words.inactive(user)
        learned_words = Word.words.is_learned(user)

        total_count = all_words.count()
        active_count = active_words.count()
        inactive_count = inactive_words.count()
        learned_count = learned_words.count()

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
        words_learned_month = learned_words.filter(updated_at__gte=month_ago).count()

        # Активность (тренировки за последние 30 дней)
        sessions = TrainingSession.objects.filter(user=user, started_at__gte=month_ago)
        sessions_count = sessions.count()
        total_trainings = (
            sessions.aggregate(total=models.Sum("total_words"))["total"] or 0
        )
        correct_trainings = (
            sessions.aggregate(total=models.Sum("correct_words"))["total"] or 0
        )

        avg_accuracy = 0
        if total_trainings > 0:
            avg_accuracy = round(correct_trainings / total_trainings * 100, 1)

        context.update(
            {
                # Статистика слов
                "total_count": total_count,
                "active_count": active_count,
                "inactive_count": inactive_count,
                "learned_count": learned_count,
                "efficiency": efficiency,
                "learning_progress": learning_progress,
                # Динамика за месяц
                "words_added_month": words_added_month,
                "words_learned_month": words_learned_month,
                # Активность тренировок
                "sessions_count": sessions_count,
                "total_trainings": total_trainings,
                "correct_trainings": correct_trainings,
                "avg_accuracy": avg_accuracy,
            }
        )

        return context


def verify_email(request, uidb64, token):
    """Вью для одтверждение электронной почты."""
    try:
        user_id = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError):
        return HttpResponseBadRequest("Некорректная ссылка подтверждения")

    if not default_token_generator.check_token(user, token):
        return HttpResponseBadRequest(
            "Ссылка недействительна или срок её действия истёк",
        )
    if user.email_verifed:
        messages.info(request, "Этот адрес электронной почты уже подтверждён.")
    else:
        user.email_verifed = True
        user.save(update_fields=["email_verifed"])
        messages.success(request, "Адрес электронной почты подтверждён.")

    return redirect("profile_info")


@login_required
@require_POST
def resend_verificaction_email(request):
    """Вью для переотправки сообщения для подтверждения электронной почты."""
    user = request.user
    if user.email_verifed:
        messages.info(request, "Адрес электронной почты уже подтверждён")

    cache_key = f"email-verification-last-sent:{user.pk}"

    if cache.get(cache_key):
        messages.warning(
            request,
            ("Письмо уже отправлено недавно. " "Попробуйте снова через 1 минуту."),
        )
    else:
        cache.set(cache_key, True, timeout=60)
        send_verification_email(
            request=request,
            user=user,
        )
        messages.success(
            request,
            "Новое письмо со ссылкой для подтверждения отправлено.",
        )

    return redirect("profile_info")
