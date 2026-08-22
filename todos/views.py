from asyncio import tasks
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import *
from .models import *
import calendar as pycal
from datetime import datetime, date, timedelta


@login_required
def todo(request):
    tasks = Task.objects.filter(user=request.user).order_by('-is_pinned', 'is_completed', 'due_date')

    # Search
    q = request.GET.get("q", "")
    if q:
        tasks = tasks.filter(name__icontains=q)

    for task in tasks:
        task.form = TaskForm(instance=task)

    add_form = TaskForm()

    today = date.today()
    current_date = datetime.now()

    # for daily,weekly,monthly,yearly

    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    month_start = today.replace(day=1)
    # First day of next month
    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    month_end = next_month - timedelta(days=1)

    year_start = today.replace(month=1, day=1)
    year_end = today.replace(month=12, day=31)

    daily_label = today.strftime("%A, %b %d")  # Thursday, Feb 19
    weekly_label = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}"  # Feb 16 - Feb 22
    monthly_label = today.strftime("%B %Y")  # February 2026
    yearly_label = today.strftime("%Y") # 2026

    daily_tasks = tasks.filter(due_date=today)
    tomorrow = today + timedelta(days=1)
    due_today_tasks = tasks.filter(due_date=today, is_completed=False)
    due_tomorrow_tasks = tasks.filter(due_date=tomorrow, is_completed=False)
    high_priority_tasks = tasks.filter(priority="high", is_completed=False)
    weekly_tasks = tasks.filter(due_date__gte=week_start, due_date__lte=week_end)
    monthly_tasks = tasks.filter(due_date__gte=month_start, due_date__lte=month_end)
    yearly_tasks = tasks.filter(due_date__gte=year_start, due_date__lte=year_end)

    daily_tasks_count = daily_tasks.count()
    daily_completed_tasks = daily_tasks.filter(is_completed=True)
    daily_pending_tasks = daily_tasks.filter(is_completed=False)
    daily_completed_tasks_count = daily_completed_tasks.count()
    daily_pending_tasks_count = daily_pending_tasks.count()

    weekly_tasks_count = weekly_tasks.count()
    weekly_completed_tasks = weekly_tasks.filter(is_completed=True)
    weekly_pending_tasks = weekly_tasks.filter(is_completed=False)
    weekly_completed_tasks_count = weekly_completed_tasks.count()
    weekly_pending_tasks_count = weekly_pending_tasks.count()

    monthly_tasks_count = monthly_tasks.count()
    monthly_completed_tasks = monthly_tasks.filter(is_completed=True)
    monthly_pending_tasks = monthly_tasks.filter(is_completed=False)
    monthly_completed_tasks_count = monthly_completed_tasks.count()
    monthly_pending_tasks_count = monthly_pending_tasks.count()

    def calculate_group_percent(group_queryset):
        total = group_queryset.count()
        if total == 0:
            return 0, 0

        completed = group_queryset.filter(is_completed=True).count()
        completed_percent = (completed / total) * 100
        remaining_percent = 100 - completed_percent

        return round(completed_percent), round(remaining_percent)

    daily_done, daily_remaining = calculate_group_percent(daily_tasks)
    weekly_done, weekly_remaining = calculate_group_percent(weekly_tasks)
    monthly_done, monthly_remaining = calculate_group_percent(monthly_tasks)
    yearly_done, yearly_remaining = calculate_group_percent(yearly_tasks)


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

    task_page = Paginator(tasks, 5).get_page(request.GET.get("page"))



    context = {
        "tasks": tasks,
        "task_page": task_page,
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
        # Time groups
        "daily_tasks": daily_tasks,
        "due_today_tasks": due_today_tasks,
        "due_today_count": due_today_tasks.count(),
        "due_tomorrow_tasks": due_tomorrow_tasks,
        "due_tomorrow_count": due_tomorrow_tasks.count(),
        "high_priority_tasks": high_priority_tasks,
        "high_priority_count": high_priority_tasks.count(),
        "weekly_tasks": weekly_tasks,
        "monthly_tasks": monthly_tasks,
        "yearly_tasks": yearly_tasks,

        "daily_done_percent": daily_done,
        "daily_remaining_percent": daily_remaining,

        "weekly_done_percent": weekly_done,
        "weekly_remaining_percent": weekly_remaining,

        "monthly_done_percent": monthly_done,
        "monthly_remaining_percent": monthly_remaining,

        "yearly_done_percent": yearly_done,
        "yearly_remaining_percent": yearly_remaining,

        "daily_tasks_count": daily_tasks_count,
        "daily_completed_tasks": daily_completed_tasks,
        "daily_pending_tasks": daily_pending_tasks,
        "daily_pending_tasks_count": daily_pending_tasks_count,
        "daily_completed_tasks_count": daily_completed_tasks_count,

        "weekly_tasks_count": weekly_tasks_count,
        "weekly_completed_tasks": weekly_completed_tasks,
        "weekly_pending_tasks": weekly_pending_tasks,
        "weekly_pending_tasks_count": weekly_pending_tasks_count,
        "weekly_completed_tasks_count": weekly_completed_tasks_count,

        "monthly_tasks_count": monthly_tasks_count,
        "monthly_completed_tasks": monthly_completed_tasks,
        "monthly_pending_tasks": monthly_pending_tasks,
        "monthly_pending_tasks_count": monthly_pending_tasks_count,
        "monthly_completed_tasks_count": monthly_completed_tasks_count,

        "daily_label": daily_label,
        "weekly_label": weekly_label,
        "monthly_label": monthly_label,
        "yearly_label": yearly_label,
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

@login_required
def toggle_pin(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.is_pinned = not task.is_pinned
    task.save()
    return redirect('todolist')
