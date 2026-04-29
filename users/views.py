from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Profile
from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import RegisterForm


class RegistrationView(CreateView):
    """Вью для регистрации"""

    template_name = 'registration/registration.html'
    form_class = RegisterForm
    success_url = 'login'


class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'users/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.request.user.profile


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'users/profile_edit.html'
    fields = ('avatar', 'bio',)

    def get_object(self):
        return self.request.user.profile

    def get_success_url(self):
        return reverse_lazy('profile')
