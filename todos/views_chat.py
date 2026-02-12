from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .ai_command_parser import parse_todo_command
from .command_handlers import TodoCommandHandler
from .models import Task


@login_required
@require_POST
@csrf_exempt
def todo_chat_command(request):
    try:
        # Parse request
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({
                'success': False,
                'message': 'Please enter a command'
            })

        # Parse command using Groq AI
        command_data = parse_todo_command(user_message, request.user.username)
        action = command_data.get('action', 'unknown')

        # Initialize command handler
        handler = TodoCommandHandler(request.user)

        # Execute command based on action
        if action == 'delete':
            result = handler.delete_task(command_data.get('task_identifier', ''))

        elif action == 'complete':
            result = handler.complete_task(command_data.get('task_identifier', ''))

        elif action == 'uncomplete':
            result = handler.uncomplete_task(command_data.get('task_identifier', ''))

        elif action == 'add':
            # Parse due date if provided
            due_date = None
            if command_data.get('due_date'):
                due_date = handler.parse_due_date(command_data['due_date'])

            result = handler.add_task(
                task_name=command_data.get('task_name', ''),
                due_date=due_date,
                priority=command_data.get('priority', 'medium'),
                option=command_data.get('option', 'option1')
            )

        elif action == 'list':
            result = handler.list_tasks(
                status=command_data.get('status'),
                priority=command_data.get('priority'),
                option=command_data.get('option')
            )

        elif action == 'clear_completed':
            result = handler.clear_completed()

        else:
            # for Unknown command
            result = {
                'success': False,
                'message': "I didn't understand that. Try commands like:\n"
                           "• 'delete buy milk'\n"
                           "• 'complete task 5'\n"
                           "• 'add finish report tomorrow'\n"
                           "• 'show my tasks'\n"
                           "• 'clear completed tasks'"
            }

        return JsonResponse({
            'success': result.get('success', False),
            'message': result.get('message', ''),
            'action': action,
            'tasks': result.get('tasks', [])
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid request format'
        }, status=400)
    except Exception as e:
        print(f"Chat command error: {e}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred processing your command'
        }, status=500)


@login_required
def get_tasks_json(request):
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')[:20]
    tasks_data = []

    for task in tasks:
        tasks_data.append({
            'id': task.id,
            'name': task.name,
            'completed': task.is_completed,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'priority': task.priority,
            'option': task.option,
            'days_left': task.days_left
        })

    return JsonResponse({'tasks': tasks_data})