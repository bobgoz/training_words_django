from django.urls import path, include
from django.views.generic.base import TemplateView

from .views import RegistrationView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='registration'),
]
