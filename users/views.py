from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from .forms import RegisterForm
from .models import Profile


class RegistrationView(CreateView):
    """Вью для регистрации"""

    template_name = 'registration/registration.html'
    form_class = RegisterForm
    success_url = 'login'


class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'users/profile_base.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.request.user.profile


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'users/profile_edit.html'
    fields = (
        'avatar',
        'bio',
    )

    def get_object(self):
        return self.request.user.profile

    def get_success_url(self):
        return reverse_lazy('profile')


class ProfileInfoView(LoginRequiredMixin, DetailView):
    """Информация о профиле"""

    model = Profile
    template_name = 'users/profile_info.html'

    def get_object(self):
        return self.request.user.profile
