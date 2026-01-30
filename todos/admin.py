from django.contrib import admin

from todos.models import *

# Register your models here.
# Option Admin
@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('option_name',)  # Show name in list
    search_fields = ('option_name',)  # Allow searching by name
    ordering = ('option_name',)  # Order alphabetically

# Priority Admin
@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
    list_display = ('priority_name',)
    search_fields = ('priority_name',)
    ordering = ('priority_name',)

# Task Admin
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'option', 'priority', 'is_completed', 'due_date', 'created_at')
    #list_filter = ('priority', 'option', 'is_completed', 'due_date')  # Filters in sidebar
    search_fields = ('name', 'option__option_name', 'priority__priority_name')  # Search across related fields
    ordering = ('-created_at',)  # Newest tasks first





