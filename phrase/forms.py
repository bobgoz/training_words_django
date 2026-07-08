from django import forms

from .models import Phrase


class CreatePhraseForm(forms.ModelForm):
    """Форма для создания словосочетания."""

    class Meta:
        model = Phrase
        fields = (
            "phrase",
            "is_active",
        )
