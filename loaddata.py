import json
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'training_words.settings')
django.setup()
from training.models import Word
from django.contrib.auth import get_user_model

User = get_user_model()

with open('Word.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    print(data)


def loaddata():
    objects = []
    for item in data:
        objects.append(
            Word(
                pk=item['id'],
                definition=item['description'],
                is_new=item['is_new'],
                is_unknown=item['is_unknown'],
                user_id=item['user_id'],
                word=item['word'],
            )
        )
    Word.objects.bulk_create(objects)


loaddata()
