from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    TAG_CHOICES = [
        ('personal', 'Personal'),
        ('work', 'Work'),
        ('ideas', 'Ideas'),
        ('important', 'Important'),
    ]
    tag = models.CharField(max_length=20, choices=TAG_CHOICES, default='personal')
    pinned = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-pinned', '-created_at']

