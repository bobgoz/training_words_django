from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('me/', views.ProfileView.as_view(), name='profile'),
    path('me/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('me/info/', views.ProfileInfoView.as_view(), name='profile_info'),
]
