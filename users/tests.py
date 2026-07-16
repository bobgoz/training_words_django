from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class TestUser(TestCase):
    """Тестирование приложения users"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username="test_user",
            password="password",
        )
        cls.auth_client = Client()
        cls.auth_client.login(
            username="test_user",
            password="password",
        )
        cls.urlpatterns = [
            "register",
            "profile",
            "profile_info",
            "profile_edit",
        ]

    # def test_urls(self):
    #     for url in self.urlpatterns:
    #         with self.subTest(url=reverse(url)):
    #             response = self.auth_client.get(url)
    #             self.assertEqual(response.status_code, 200)
