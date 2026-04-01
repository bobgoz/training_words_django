from django import forms

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
