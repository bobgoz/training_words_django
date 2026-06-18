from celery import shared_task
from django.core.files.base import ContentFile
from training.models import Word

@shared_task
def upload_image_to_dropbox(word_id):
    try:
        word = Word.objects.get(id=word_id)
        if word.image:
            # Пересохраняем картинку для загрузки в Dropbox
            with word.image.open('rb') as f:
                word.image.save(word.image.name, ContentFile(f.read()), save=True)
    except Exception as e:
        print(f"Error uploading image: {e}")