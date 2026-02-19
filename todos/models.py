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
        ('option1', 'Personal'),
        ('option2', 'Work / Professional'),
        ('option3', 'Home / Chores'),
        ('option4', 'Study / Education'),
        ('option5', 'Health / Fitness'),
        ('option6', 'Shopping / Errands'),
        ('option7', 'Finance / Bills'),
        ('option8', 'Social / Relationships'),
        ('option9', 'Travel / Leisure'),
        ('option10', 'Events / Appointments'),
        ('option11', 'Goals / Projects'),
        ('option12', 'Hobbies / Creativity'),
        ('option13', 'Self-improvement'),
        ('option14', 'Community / Volunteering'),
        ('option15', 'Miscellaneous / Urgent'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    name = models.CharField(max_length=100)
    is_completed = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
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
