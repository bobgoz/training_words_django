from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class RegisterForm(UserCreationForm):
    """Форма регистрации и авторизации"""

    email = forms.EmailField(
        label="Электронная почта",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
        )


class EmailAuthenticationForm(AuthenticationForm):
    """Форма входа по адресу электронной почты."""

    username = forms.EmailField(
        label="Электронная почта",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "autocomplete": "email",
                "autofocus": True,
            }
        ),
    )
