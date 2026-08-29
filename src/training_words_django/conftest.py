"""Модуль, содержащий  фикстуры для Pytest."""

from django.test.client import Client
from django.urls import reverse
from pytest import fixture

from training_words_django.phrase.models import Phrase
from training_words_django.training.models import Word


# Объекты
@fixture
def author(django_user_model):
    """Первый автор."""
    return django_user_model.objects.create(username="Василий")


@fixture
def second_author(django_user_model):
    """Второй автор."""
    return django_user_model.objects.create(username="Петр")


@fixture
def auth_client(author):
    """Авторизованный клиент."""
    client = Client()
    client.force_login(author)
    return client


@fixture
def second_auth_client(second_author):
    """Второй авторизованный клиент."""
    client = Client()
    return client.force_login(second_author)


@fixture
def no_auth_client():
    """Неавторизованный клиент."""
    return Client()


@fixture
def word_mass_create(author):
    """Массовое  создание (10) активных слов."""
    words = [
        Word(
            word=f"word_{i}",
            user=author,
            is_active=True,
        )
        for i in range(10)
    ]
    return Word.objects.bulk_create(words)


@fixture
def word_mass_create_noactive(author):
    """Массовое  создание (10) неактивных слов."""
    words = [
        Word(
            word=f"word_{i}",
            user=author,
            is_active=False,
        )
        for i in range(10)
    ]
    return Word.objects.bulk_create(words)


@fixture
def word_mass_create_islearned(author):
    """Массовое  создание (10) изученных слов."""
    words = [
        Word(
            word=f"word_{i}",
            user=author,
            is_learned=True,
        )
        for i in range(10)
    ]
    return Word.objects.bulk_create(words)


@fixture
def word_ru(author):
    """Русское слово."""
    return Word.objects.create(
        word="молоко",
        user=author,
    )


@fixture
def word_en(author):
    """Английское слово."""
    return Word.objects.create(
        word="milk",
        user=author,
    )


@fixture
def form_data(author):
    """Данные формы."""
    return {
        "word": "слово",
        "user": author,
    }


@fixture
def pk_for_args(word_ru):
    """Id объекта."""
    return word_ru.id


# Юрлы
@fixture
def login_url():
    """Юрл входа в аккаунт."""
    return reverse("login")


@fixture
def register_url():
    """Юрл регистрации."""
    return reverse("register")


@fixture
def logout_url():
    """Юрл выхода из аккаунта."""
    return reverse("logout")


@fixture
def inactive_words_url():
    """Юрл для неактивных слов."""
    return reverse("inactive_words")


@fixture
def word_detail_url(word_ru):
    """Юрл с детальным отображением объекта слова."""
    return word_ru.get_absolute_url()


@fixture
def edit_word_url(pk_for_args):
    """Юрл для редактирования слова."""
    return reverse("edit_word", args=(pk_for_args,))


@fixture
def delete_word_url(pk_for_args):
    """Юрл для удаления слова."""
    return reverse("delete_word", args=(pk_for_args,))


@fixture
def search_url():
    """Юрл для поиска слов."""
    return reverse("search")


@fixture
def create_url():
    """Юрл создания слова."""
    return reverse("add_word")


@fixture
def noactive_url():
    """Юрл неактивных слов."""
    return reverse("inactive_words")


# Фикстуры приложения Phrase
@fixture
def phrase_urls():
    """Возвращает имена юрлов приложения phrase."""
    return (
        "add_phrase",
        "phrase_manager",
        "active_phrases",
        "inactive_phrases",
        "learned_phrases",
    )


@fixture
def phrase_edit_url(phrase_object):
    """Юрл для редактирования объектов."""
    return reverse("edit_phrase", args=(phrase_object.pk,))


@fixture
def add_phrase_url(phrase_urls):
    """Юрл для создания объекта."""
    return reverse("add_phrase")


@fixture
def phrase_object(author):
    """Объект Phrase."""
    return Phrase.objects.create(
        user=author,
        phrase="Большой-большой секрет",
    )


@fixture
def phrase_detail(phrase_object):
    """Детальное  отображение  объекта."""
    return phrase_object.get_absolute_url()


@fixture
def phrase_form_data():
    """Данные формы для объекта словосочетаний."""
    return dict(
        phrase="Авантюра",
    )
