from django import forms

from todos.models import *


class TaskForm(forms.ModelForm):
    OPTION_CHOICES = [
        ('option1', 'Work'),
        ('option2', 'Study'),
        ('option3', 'Travel'),
        ('option4', 'Family'),
        ('option5', 'Shopping'),
        ('option6', 'Exercise'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    is_completed = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            }
        )
    )

    option = forms.ChoiceField(
        choices=OPTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Task
        widgets = {
            'due_date': forms.DateInput(attrs={'class': 'form-control'}),
        }
        exclude = ('user',)

