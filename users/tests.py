import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

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

    def test_profile_created_for_multiple_users(self):
        """Проверяет, что профили создаются для всех новых пользователей"""
        users = [
            User.objects.create_user(username=f'testuser_{i}')
            for i in range(5)
        ]

        for user in users:
            assert hasattr(user, 'profile')
            assert user.profile.pk is not None


@pytest.mark.django_db
class TestUrls:
    """Тестирование маршрутов приложения users"""

    @pytest.mark.parametrize(
        'url_name, expected_status,',
        [
            ('register', 200),
            ('profile', 302),  # 302 — редирект на логин для неавторизованных
            ('edit_profile', 302),
        ],
    )
    def test_urls_unauthorized(self, client, url_name, expected_status):
        """Тестирование доступности URL для неавторизованного пользователя"""
        url = reverse(url_name)
        response = client.get(url)
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        'url_name, expected_status,',
        [
            ('register', 200),
            ('profile', 200),
            ('edit_profile', 200),
        ],
    )
    def test_urls_authorized(self, client, url_name, expected_status):
        """Тестирование доступности URL для авторизованного пользователя"""

        User.objects.create_user(username='testuser', password='testpass123')
        client.login(username='testuser', password='testpass123')

        url = reverse(url_name)
        response = client.get(url)
        assert response.status_code == expected_status
