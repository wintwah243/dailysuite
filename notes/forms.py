from django import forms
from .models import Note


class NoteForm(forms.ModelForm):
    tag = forms.ChoiceField(
        choices=[
            ('personal', 'Personal'),
            ('work', 'Work'),
            ('ideas', 'Ideas'),
            ('important', 'Important'),
        ],
        required=False,
        initial='personal'
    )
    pinned = forms.BooleanField(required=False, initial=False)

    class Meta:
        model = Note
        fields = ['title', 'content']