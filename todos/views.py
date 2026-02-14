from asyncio import tasks
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
import calendar as pycal
from datetime import datetime, date


@login_required
def todo(request):
    tasks = Task.objects.filter(user=request.user)

    for task in tasks:
        task.form = TaskForm(instance=task)

    add_form = TaskForm()

    today = date.today()
    current_date = datetime.now()

    cal = pycal.Calendar(firstweekday=0)
    month_dates = cal.monthdatescalendar(current_date.year, current_date.month)

    calendar_days = []
    for week in month_dates:
        for day in week:
            if day.month == current_date.month:
                calendar_days.append(day.day)
            else:
                calendar_days.append(0)

    task_days = []
    for task in tasks:
        if task.due_date and task.due_date.month == current_date.month and task.due_date.year == current_date.year:
            task_days.append(task.due_date.day)
    task_days = list(set(task_days))

    completed_count = tasks.filter(is_completed=True).count()
    pending_count = tasks.filter(is_completed=False).filter(
        Q(due_date__gte=today) | Q(due_date__isnull=True)
    ).count()

    overdue_count = 0
    for task in tasks.filter(is_completed=False):
        if task.due_date and task.due_date < today:
            overdue_count += 1

    # Task groups
    inprogress = tasks.filter(is_completed=False).filter(
        Q(due_date__gte=today) | Q(due_date__isnull=True)
    )
    done = tasks.filter(is_completed=True)
    overdue = tasks.filter(is_completed=False, due_date__lt=today)

    # Percentages
    total_tasks = tasks.count()

    if total_tasks > 0:
        done_percent = (completed_count / total_tasks) * 100
        inprogress_percent = (pending_count / total_tasks) * 100
        overdue_percent = (overdue_count / total_tasks) * 100
    else:
        done_percent = 0
        inprogress_percent = 0
        overdue_percent = 0

    # Search
    q = request.GET.get("q", "")
    if q:
        tasks = tasks.filter(name__icontains=q)

    context = {
        "tasks": tasks,
        "add_form": add_form,
        "today": today,
        "current_date": current_date,
        "week_days": ["M", "T", "W", "T", "F", "S", "S"],
        "calendar_days": calendar_days,
        "task_days": task_days,
        "completed_count": completed_count,
        "pending_count": pending_count,
        "overdue_count": overdue_count,
        "inprogress": inprogress,
        "done": done,
        "overdue": overdue,
        "done_percent": round(done_percent),
        "inprogress_percent": round(inprogress_percent),
        "overdue_percent": round(overdue_percent),
        "query": q,
    }

    return render(request, "todos/todohome.html", context)


@login_required
def addtask(request):
    if request.method == "POST":
        taskform = TaskForm(request.POST)
        if taskform.is_valid():
            task = taskform.save(commit=False)
            task.user = request.user
            task.save()

    return redirect("todolist")


@login_required
def updatetask(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)

    if request.method == "POST":
        taskform = TaskForm(request.POST, instance=task)
        if taskform.is_valid():
            taskform.save()

    return redirect("todolist")


@login_required
def deletetask(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    task.delete()
    return redirect("todolist")


@login_required
def toggle_task(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    task.is_completed = not task.is_completed
    task.save()
    return redirect("todolist")

# @login_required
# def toggle_pin(request, id):
#     task = get_object_or_404(Task, id=id, user=request.user)
#     task.is_pinned = not task.is_pinned
#     task.save()
#     return redirect("todolist")

