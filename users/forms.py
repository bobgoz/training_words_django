from django import forms

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class RegisterForm(UserCreationForm):
    """Форма регистрации и авторизации"""

    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='Имя',
        widget=forms.TextInput(attrs={'placeholder': 'Введите имя'}),
    )

    last_name = forms.CharField(
        max_length=30,
        required=True,
        label='Фамилия',
        widget=forms.TextInput(attrs={'placeholder': 'Введите фамилию'}),
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']
