from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth import get_user_model
from django.views.generic import FormView
from django.contrib import messages

from .forms import RegisterForm, SimplePasswordForm

User = get_user_model()


class RegistrationView(CreateView):
    """Вью для регистрации"""

    template_name = 'registration/registration.html'
    form_class = RegisterForm
    success_url = 'login'


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
