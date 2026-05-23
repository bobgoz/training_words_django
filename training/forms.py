from django import forms

from .constants import COUNT_RANDOM_WORDS, COUNT_WORDS_FOR_ACTIVATE
from .models import Word


class CreateWordForm(forms.ModelForm):
    """Форма для создания слова"""

    class Meta:
        model = Word
        fields = (
            'word',
            'definition',
            'example',
            'image',
            'is_active',
        )
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'word': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'autofocus': True,
                    'autocomplete': 'off',
                    'placeholder': 'Введите слово',
                }
            ),
        }


class EditWordForm(forms.ModelForm):
    """Форма редактирования слова"""

    class Meta:
        model = Word
        fields = (
            'word',
            'definition',
            'example',
            'is_active',
            'is_hard',
            'image',
        )


class TrainingSettingsForm(forms.Form):
    """Форма настройки тренировки"""

    WORD_TYPE_CHOICES = [
        ('all', 'Активные слова'),
        ('hard', 'Только сложные'),
        ('learned', 'Только изученные'),
        ('random', 'Случайные'),
    ]

    word_type = forms.ChoiceField(
        choices=WORD_TYPE_CHOICES,
        widget=forms.RadioSelect,
        initial=WORD_TYPE_CHOICES[0],
        label='Тип слов',
    )

    count = forms.IntegerField(
        min_value=5,
        max_value=100,
        initial=10,
        label='Количество слов',
        help_text='Сколько слов хотите повторить? (5-50)',
    )
