"""Модуль  тестирования."""

from http import HTTPStatus

from django.urls import reverse

from .models import Phrase


class TestPhraseUrl:
    """Тестирование маршрутов приложения phrase."""

    def test_urls(self, auth_client, phrase_urls):
        """Тестирование маршрутов приложения phrase."""
        for url in phrase_urls:
            url = reverse(url)
            response = auth_client.get(url)
            assert response.status_code == HTTPStatus.OK

    def test_detail_url(self, auth_client, phrase_detail):
        """Тестирование детального отображения объекта."""
        response = auth_client.get(phrase_detail)
        assert response.status_code == HTTPStatus.OK

    def test_create_phrase(
        self,
        auth_client,
        add_phrase_url,
        phrase_form_data,
    ):
        """Тестирование добавления объекта."""
        response = auth_client.post(add_phrase_url, data=phrase_form_data)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == add_phrase_url
        assert Phrase.objects.filter(**phrase_form_data).exists()

    # def test_another_user_cannot_edit_phrase_object(
    #     self,
    #     auth_client,
    #     phrase_edit_url,
    #     phrase_object,
    #     second_author,
    #     phrase_form_data,
    # ):
    #     phrase_object.user = second_author
    #     phrase_object.save()
    #     response = auth_client.post(
    #         phrase_edit_url, data=phrase_form_data
    #     )
    #     assert response.status_code == 200
