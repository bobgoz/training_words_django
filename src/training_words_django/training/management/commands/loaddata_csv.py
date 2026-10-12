"""Модуль с кастомной командой для пополнения БД данными."""

import csv
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from phrase.models import Phrase
from training.models import Word

BASE_DIR = Path(__file__).parent

User = get_user_model()


class Command(BaseCommand):
    """Класс кастомной команды."""

    help = "Импорт объектов из CSV-файла"

    def add_arguments(self, parser):
        """Добавляет аргументы командной строки для импорта данных."""
        parser.add_argument(
            "--username",
            type=str,
            default="admin",
            help="Имя пользователя (по умолчанию: admin)",
        )

    def handle(self, *args, **options):
        """Выполняет импорт данных из CSV-файлов.

        Очищает БД, создаёт суперпользователя и загружает
        слова и словосочетания.
        """
        # Очищаем все записи в таблице.
        User.objects.all().delete()
        Phrase.objects.all().delete()
        Word.objects.all().delete()

        username = options["username"]

        password = "password"

        # Создание пользователя
        user = User.objects.create_superuser(
            username=username,
            password=password,
        )

        # Чтение CSV.
        try:
            # Чтение из файла words.csv
            path_to_words_file = BASE_DIR / "words.csv"
            with open(path_to_words_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                count = 0

                for row in reader:
                    word_from_csv = row.get("word").strip()

                    # Создаём слово
                    Word.objects.create(
                        user=user,
                        word=word_from_csv,
                        definition=row.get("definition", "").strip(),
                    )
                    count += 1

                self.stdout.write(self.style.SUCCESS(f"Создано {count} слов."))

                # Чтение из файла phrase.csv
                path_to_phrases_file = BASE_DIR / "phrases.csv"
                with open(path_to_phrases_file, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    count = 0
                    for row in reader:
                        phrase_from_csv = row.get("phrase").strip()
                        Phrase.objects.create(
                            user=user,
                            phrase=phrase_from_csv,
                        )
                        count += 1

                self.stdout.write(
                    self.style.SUCCESS(f"Создано {count} словосочетаний.")
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Создан пользователь {username} с правами " "администратора"
                    )
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        "Данные для входа:"
                        f"\nusername: {username}, пароль: {password}"
                    )
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
