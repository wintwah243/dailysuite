from django.contrib import admin

from todos.models import *

# Register your models here.

# Task Admin
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'option', 'priority', 'is_completed', 'due_date', 'created_at')
    list_filter = ('priority', 'option', 'is_completed', 'due_date')  # Filters in sidebar
    search_fields = ('name', 'option', 'priority')  # Search across related fields
    ordering = ('-created_at',)  # Newest tasks first





