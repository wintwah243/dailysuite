from django import forms

from todos.models import *


class TaskForm(forms.ModelForm):
    OPTION_CHOICES = [
        ('Personal', 'Personal'),
        ('Work / Professional', 'Work / Professional'),
        ('Home / Chores', 'Home / Chores'),
        ('Study / Education', 'Study / Education'),
        ('Health / Fitness', 'Health / Fitness'),
        ('Shopping / Errands', 'Shopping / Errands'),
        ('Finance / Bills', 'Finance / Bills'),
        ('Social / Relationships', 'Social / Relationships'),
        ('Travel / Leisure', 'Travel / Leisure'),
        ('Events / Appointments', 'Events / Appointments'),
        ('Goals / Projects', 'Goals / Projects'),
        ('Hobbies / Creativity', 'Hobbies / Creativity'),
        ('Self-improvement', 'Self-improvement'),
        ('Community / Volunteering', 'Community / Volunteering'),
        ('Miscellaneous / Urgent', 'Miscellaneous / Urgent'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    name = forms.CharField(required=True,label="", widget=forms.TextInput(attrs={'class': 'form-control w-full text-2xl py-2','placeholder': 'Task Name','id': 'task-name-input'}))
    is_completed = forms.BooleanField(required=False, label="Status", widget=forms.CheckboxInput(attrs={'class' : 'h-4 w-4'}))
    due_date = forms.DateField(
        required=True, label="Due date",
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            }
        )
    )

    option = forms.ChoiceField(
        choices=OPTION_CHOICES,
        initial=OPTION_CHOICES[0][0],
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

