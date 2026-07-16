from django.test.client import Client
from django.urls import reverse
from pytest import fixture

from training.models import Word


# Объекты
@fixture
def author(django_user_model):
    """Фикстура автора"""
    return django_user_model.objects.create(username="Василий")


@fixture
def auth_client(author):
    """Авторизованный клиент"""
    client = Client()
    client.force_login(author)
    return client


@fixture
def no_auth_client():
    """Неавторизованный клиент"""
    return Client()


@fixture
def word_mass_create(author):
    """
    Массовое  создание (10)
    активных слов.
    """
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
    """
    Массовое  создание (10)
    неактивных слов.
    """
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
    """
    Массовое  создание (10)
    изученных слов.
    """
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
    """Русское слово"""
    return Word.objects.create(
        word="молоко",
        user=author,
    )


@fixture
def word_en(author):
    """Английское слово"""
    return Word.objects.create(
        word="milk",
        user=author,
    )


@fixture
def new_word(author):
    """Новый объект слова"""
    return Word.objects.create(
        word="Вода",
        user=author,
    )


@fixture
def form_data(author, new_word):
    """Данные формы"""
    return {
        "word": "слово",
        "user": author,
    }


@fixture
def pk_for_args(word_ru):
    """id объекта"""
    return word_ru.id


# Юрлы
@fixture
def login_url():
    return reverse("login")


@fixture
def register_url():
    return reverse("register")


@fixture
def logout_url():
    return reverse("logout")


@fixture
def admin_url():
    return reverse("admin")


@fixture
def mark_as_active_url():
    return reverse("mark_as_active")


@fixture
def mark_as_inactive_url():
    return reverse("mark_as_inactive")


@fixture
def training_url():
    return reverse("training")


@fixture
def inactive_words_url():
    return reverse("inactive_words")


@fixture
def training_random_active_url():
    return reverse("training_random")


@fixture
def detail_url(pk_for_args):
    return reverse("detail", args=(pk_for_args,))


@fixture
def edit_word_url(pk_for_args):
    return reverse("edit_word", args=(pk_for_args,))


@fixture
def delete_word_url(pk_for_args):
    return reverse("delete_word", args=(pk_for_args,))


@fixture
def search_url():
    return reverse("search")


@fixture
def random_url():
    return reverse("training_random")


@fixture
def create_url():
    """Юрл создания слова"""
    return reverse("add_word")


@fixture
def noactive_url():
    """Юрл неактивных слов"""
    return reverse("inactive_words")
