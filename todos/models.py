from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Task(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tasks"
    )

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

    @property
    def days_left(self):
        if self.due_date:
            today = timezone.now().date()
            return (self.due_date - today).days
        return None

    @property
    def days_left_abs(self):
        return abs(self.days_left) if self.days_left is not None else None

    def __str__(self):
        return self.name
