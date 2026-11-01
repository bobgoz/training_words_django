"""Касстомные бекенды аутентификации."""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailBackend(ModelBackend):
    """Аутентифицирует пользователя по адресу электронной почты."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        email = username

        if not email or not password:
            return None

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Выполняем хеширование для снижения разницы во времени ответа.
            User().setз_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
