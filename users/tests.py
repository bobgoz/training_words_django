from http import HTTPStatus

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from pytest_lazy_fixtures import lf

from .models import Profile

User = get_user_model()


@pytest.mark.django_db
class TestProfileCreation:
    def test_profile_created_with_user(self):
        """
        Проверяет, что при создании пользователя
        автоматически создаётся профиль.
        """
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )

        # Проверяем, что профиль существует
        assert hasattr(user, 'profile'), 'Профиля пользователя нет'
        assert isinstance(user.profile, Profile)
        assert user.profile.pk is not None

    def test_profile_has_correct_user_link(self):
        """Проверяет, что профиль привязан к правильному пользователю"""
        user = User.objects.create_user(username='testuser2')

        assert user.profile.user == user


@pytest.mark.django_db
class TestUrls:
    """Тестирование маршрутов приложения users"""

    @pytest.mark.parametrize(
        'url_name, client, expected_status,',
        [
            ('register', lf('no_auth_client'), HTTPStatus.OK),
            ('profile', lf('auth_client'), HTTPStatus.OK),
            ('profile_edit', lf('auth_client'), HTTPStatus.OK),
            ('profile_info', lf('auth_client'), HTTPStatus.OK),
        ],
    )
    def test_urls_unauthorized(
        self,
        client,
        url_name,
        expected_status,
    ):
        """Тестирование доступности URL для неавторизованного пользователя"""
        url = reverse(url_name)
        response = client.get(url)
        assert response.status_code == expected_status
