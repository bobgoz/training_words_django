from django.shortcuts import render
from django.views.generic import CreateView

from .forms import RegisterForm


class RegistrationView(CreateView):
    """Вью для регистрации"""

    template_name = 'registration/registration.html'
    form_class = RegisterForm
    success_url = '/'
