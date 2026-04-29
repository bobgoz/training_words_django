from django.urls import path, include
from django.views.generic.base import TemplateView

from . import views

urlpatterns = [
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('me/', views.ProfileView.as_view(), name='profile'),
    path('me/edit/', views.ProfileEditView.as_view(), name='edit_profile'),
]
