from django.db import models

# Create your models here.

class Option(models.Model):
    option_name = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = "Options"
        ordering = ['option_name']
    def __str__(self):
        return self.option_name

class Priority(models.Model):
    priority_name = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = "Priorities"
    def __str__(self):
        return self.priority_name

class Task(models.Model):
    name = models.CharField(max_length=100)
    is_completed = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    options = models.ForeignKey(Option, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    priority = models.ForeignKey(Priority, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
