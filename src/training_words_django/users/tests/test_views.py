from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class TestUser(TestCase):
    """Тестирование приложения users"""

    def setUp(self):
        self.login_url = reverse("login")
        self.register_url = reverse("register")
        self.index_url = reverse("index")
        # self.invalid_data_to_register = dict(
        #     username='test_user',
        #     email='invalid_email.ru',
        #     password='qwert',
        # )
        self.email = "valid_email@example.ru"
        self.password = "frikazoid"
        self.valid_data_to_register = dict(
            username="username",
            email=self.email,
            password1=self.password,
            password2=self.password,
        )
        self.login_data = dict(
            username=self.email,
            password=self.password,
        )

    def test_user_can_register_and_login(self):
        response_register = self.client.post(
            self.register_url,
            data=self.valid_data_to_register,
        )
        self.assertRedirects(response_register, self.login_url)

        user_exists = User.objects.filter(email=self.email).exists()
        self.assertTrue(user_exists, "Пользователя нет в БД")

        login_response = self.client.post(self.login_url, data=self.login_data)
        self.assertRedirects(login_response, self.index_url)
