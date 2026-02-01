from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *
import calendar as pycal
from datetime import datetime, date


# Create your views here.
def todo(request):
    tasks = Task.objects.all()
    for task in tasks:
        task.form = TaskForm(instance=task)
    add_form = TaskForm()

    # Calendar data calculation
    today = date.today()
    current_date = datetime.now()

    # Get month days for calendar display
    cal = pycal.Calendar(firstweekday=0)  # Monday as first day
    month_dates = cal.monthdatescalendar(current_date.year, current_date.month)

    # Flatten the calendar days (0 for days from other months)
    calendar_days = []
    for week in month_dates:
        for day in week:
            if day.month == current_date.month:
                calendar_days.append(day.day)
            else:
                calendar_days.append(0)

    # Get days that have tasks (for dot indicators)
    task_days = []
    for task in tasks:
        if task.due_date and task.due_date.month == current_date.month and task.due_date.year == current_date.year:
            task_days.append(task.due_date.day)
    task_days = list(set(task_days))  # Remove duplicates

    # Task statistics
    completed_count = tasks.filter(is_completed=True).count()
    pending_count = tasks.filter(is_completed=False).count()

    # Calculate overdue count
    overdue_count = 0
    for task in tasks.filter(is_completed=False):
        if task.due_date and task.due_date < today:
            overdue_count += 1

    context = {
        'tasks': tasks,
        'add_form': add_form,

        # Calendar context
        'today': today,
        'current_date': current_date,
        'week_days': ['M', 'T', 'W', 'T', 'F', 'S', 'S'],
        'calendar_days': calendar_days,
        'task_days': task_days,

        # Stats context
        'completed_count': completed_count,
        'pending_count': pending_count,
        'overdue_count': overdue_count,
    }

    return render(request, 'todos/todohome.html', context)


def addtask(request):
    if request.method == 'POST':
        taskform = TaskForm(request.POST)
        if taskform.is_valid():
            taskform.save()
    return redirect('todolist')


def updatetask(request, id):
    task = get_object_or_404(Task, id=id)
    if request.method == 'POST':
        taskform = TaskForm(request.POST, instance=task)
        if taskform.is_valid():
            taskform.save()
    return redirect('todolist')


def deletetask(request, id):
    task = get_object_or_404(Task, id=id)
    task.delete()
    return redirect('todolist')


def toggle_task(request, id):
    task = Task.objects.get(id=id)
    task.is_completed = not task.is_completed
    task.save()
    return redirect('todolist')