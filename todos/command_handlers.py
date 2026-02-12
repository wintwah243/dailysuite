from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Task
import re
from dateutil import parser
from django.db.models import Q


class TodoCommandHandler:
    def __init__(self, user):
        self.user = user

    def delete_task(self, task_identifier):
        # Try to find by ID first
        if str(task_identifier).isdigit():
            try:
                task = Task.objects.get(id=task_identifier, user=self.user)
                task_name = task.name
                task.delete()
                return {"success": True, "message": f"Deleted task successfully: '{task_name}'"}
            except Task.DoesNotExist:
                pass

        # If not found by ID , search by task name (case insensitive)
        tasks = Task.objects.filter(
            user=self.user,
            name__icontains=task_identifier
        )

        if not tasks.exists():
            return {"success": False, "message": f"No task found matching '{task_identifier}'"}

        if tasks.count() > 1:
            task_list = "\n".join([f"  • ID {t.id}: '{t.name}'" for t in tasks])
            return {
                "success": False,
                "message": f"Multiple tasks found. Please be more specific:\n{task_list}"
            }

        task = tasks.first()
        task_name = task.name
        task.delete()
        return {"success": True, "message": f"Deleted task successfully: '{task_name}'"}

    def complete_task(self, task_identifier):
        """Mark task as completed"""
        if str(task_identifier).isdigit():
            try:
                task = Task.objects.get(id=task_identifier, user=self.user)
                task.is_completed = True
                task.save()
                return {"success": True, "message": f"Completed task successfully: '{task.name}'"}
            except Task.DoesNotExist:
                pass

        tasks = Task.objects.filter(
            user=self.user,
            name__icontains=task_identifier,
            is_completed=False
        )

        if not tasks.exists():
            return {"success": False, f"message": f"No pending task found matching '{task_identifier}'"}

        if tasks.count() > 1:
            task_list = "\n".join([f"  • ID {t.id}: '{t.name}'" for t in tasks])
            return {
                "success": False,
                "message": f"Multiple pending tasks found. Please be more specific:\n{task_list}"
            }

        task = tasks.first()
        task.is_completed = True
        task.save()
        return {"success": True, "message": f"Completed task successfully: '{task.name}'"}

    def uncomplete_task(self, task_identifier):
        """Mark task as not completed"""
        if str(task_identifier).isdigit():
            try:
                task = Task.objects.get(id=task_identifier, user=self.user)
                task.is_completed = False
                task.save()
                return {"success": True, "message": f"Reopened task: '{task.name}'"}
            except Task.DoesNotExist:
                pass

        tasks = Task.objects.filter(
            user=self.user,
            name__icontains=task_identifier,
            is_completed=True
        )

        if not tasks.exists():
            return {"success": False, "message": f"No completed task found matching '{task_identifier}'"}

        if tasks.count() > 1:
            task_list = "\n".join([f"  • ID {t.id}: '{t.name}'" for t in tasks])
            return {
                "success": False,
                "message": f"Multiple completed tasks found. Please be more specific:\n{task_list}"
            }

        task = tasks.first()
        task.is_completed = False
        task.save()
        return {"success": True, "message": f"Reopened task: '{task.name}'"}

    def add_task(self, task_name, due_date=None, priority='medium', option='option1'):
        """Add a new task"""
        task = Task.objects.create(
            user=self.user,
            name=task_name,
            due_date=due_date,
            priority=priority,
            option=option,
            is_completed=False
        )
        return {
            "success": True,
            "message": f"Added new task successfully: '{task.name}'",
            "task": task
        }

    def list_tasks(self, status=None, priority=None, option=None):
        tasks = Task.objects.filter(user=self.user)

        if status == 'completed':
            tasks = tasks.filter(is_completed=True)
        elif status == 'pending':
            tasks = tasks.filter(is_completed=False)
        elif status == 'overdue':
            tasks = tasks.filter(is_completed=False, due_date__lt=timezone.now().date())

        if priority:
            tasks = tasks.filter(priority=priority)
        if option:
            tasks = tasks.filter(option=option)

        if not tasks.exists():
            return {"success": True, "message": "No tasks found.", "tasks": []}

        task_list = []
        message = "Your tasks:\n"
        for task in tasks[:10]:  # Limit to 10 tasks
            status_icon = "-" if task.is_completed else "-"
            due = f" (due: {task.due_date})" if task.due_date else ""
            task_list.append({
                "id": task.id,
                "name": task.name,
                "completed": task.is_completed,
                "due_date": task.due_date
            })
            message += f"  {status_icon} '{task.name}'{due}\n"

        if tasks.count() > 10:
            message += f"  ... and {tasks.count() - 10} more tasks"

        return {"success": True, "message": message, "tasks": task_list}

    def clear_completed(self):
        completed_tasks = Task.objects.filter(user=self.user, is_completed=True)
        count = completed_tasks.count()
        completed_tasks.delete()
        return {"success": True, "message": f"Deleted {count} completed task{'s' if count != 1 else ''}"}

    def parse_due_date(self, date_string):
        if not date_string:
            return None

        today = timezone.now().date()
        date_string = date_string.lower().strip()

        # Handle relative dates
        if date_string == 'today':
            return today
        elif date_string == 'tomorrow':
            return today + timedelta(days=1)
        elif date_string == 'next week':
            return today + timedelta(days=7)
        elif 'day' in date_string and any(char.isdigit() for char in date_string):
            # Handle "in X days"
            match = re.search(r'in\s+(\d+)\s+days?', date_string)
            if match:
                days = int(match.group(1))
                return today + timedelta(days=days)

        # Try to parse with dateutil
        try:
            parsed_date = parser.parse(date_string, fuzzy=True).date()
            return parsed_date
        except:
            return None