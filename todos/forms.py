from django import forms

from todos.models import *


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name','is_completed','due_date','priority','option']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'})
        }
