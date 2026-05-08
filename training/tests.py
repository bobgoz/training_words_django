from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_lazy_fixtures import lf

from training.models import Word


@pytest.mark.django_db
class TestWordLogic:
    """Тестирование логики тренажера"""

    def test_word_ru(self, client, word_ru):
        """Проверка, что слово относится к категории русских"""
        assert word_ru.language == 'ru', 'Слово не имеет категории "ru".'

    def test_word_en(self, word_en):
        """Проверка, что слово относится к категории английских"""
        assert word_en.language == 'en', 'Слово не имеет категории "en".'

    def test_random_url(self, word_ru, author, random_url, auth_client):
        """Тестирование логики страницы random"""
        response = auth_client.get(random_url)
        assert response.status_code == HTTPStatus.OK
        assert Word.objects.filter(
            user_id=author.id,
            is_active=False,
        ).exists()


@pytest.mark.django_db
class TestWordUrls:
    """Тестирование роутеров"""

    TRAINING_URLS = (
        'training',
        'training_hard',
        'training_no_active',
        'training_random',
    )

    @pytest.mark.parametrize('name', TRAINING_URLS)
    def test_url_for_auth_client(self, auth_client, name):
        """
        Тестирование роутеров приложения training
        для  авторизованного пользователя.
        """
        url = reverse(name)
        response = auth_client.get(url)
        assert response.status_code == HTTPStatus.OK

    @pytest.mark.parametrize('name', TRAINING_URLS)
    def test_url_for_anonim_client(self, client, name):
        """
        Тестирование роутеров приложения training
        для неавторизованного пользователя.
        """
        url = reverse(name)
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND

    def test_edit_url(
        self,
        auth_client,
        edit_word_url,
        word_ru,
        detail_url,
        form_data,
    ):
        """Дотошное тестирование редактирования слов"""

        response = auth_client.get(detail_url)
        word_obj = response.context['word']
        assert word_obj.word == word_ru.word
        # Редактирование слова
        edit_response = auth_client.post(edit_word_url, data=form_data)
        assert edit_response.status_code == 302

        response = auth_client.get(detail_url)
        word_obj = response.context['word']
        assert word_obj.word != word_ru.word
