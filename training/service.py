"""Сервисная логика."""

from eng_to_ru import Translator


def translator(word) -> str:
    """Перевод английского слова в русское."""
    translator = Translator()
    return translator.run(word)
