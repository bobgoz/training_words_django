import csv
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from phrase.models import Phrase
from training.models import Word

BASE_DIR = Path(__file__).parent

User = get_user_model()


class Command(BaseCommand):
    help = 'Импорт объектов из CSV-файла'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Имя пользователя (по умолчанию: admin)',
        )

    def handle(self, *args, **options):
        # Очищаем все записи в таблице.
        User.objects.all().delete()
        Phrase.objects.all().delete()
        Word.objects.all().delete()

        username = options['username']

        password = 'frikazoid'

        # Создание пользователя
        user = User.objects.create_user(
            username=username,
            password=password,
        )

        # Чтение CSV.
        try:
            # Чтение из файла words.csv
            file_path = BASE_DIR / 'words.csv'
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0

                for row in reader:
                    word_from_csv = row.get('word').strip()

                    # Создаём слово
                    Word.objects.create(
                        user=user,
                        word=word_from_csv,
                        definition=row.get('definition', '').strip(),
                    )
                    count += 1

                self.stdout.write(self.style.SUCCESS(f'Создано {count} слов.'))

                # Чтение из файла phrase.csv
                file_path = BASE_DIR / 'phrases.csv'
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    count = 0
                    for row in reader:
                        phrase_from_csv = row.get('phrase').strip()
                        Phrase.objects.create(
                            user=user,
                            phrase=phrase_from_csv,
                        )
                        count += 1

                self.stdout.write(
                    self.style.SUCCESS(f'Создано {count} словосочетаний.')
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Данные для входа:\nusername: {username}, пароль: {password}'
                    )
                )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Файл не найден: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))
