from django.db import models

# Create your models here.

class Task(models.Model):
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
    name = models.CharField(max_length=100)
    is_completed = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    option = models.CharField(max_length=50, choices=OPTION_CHOICES)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
