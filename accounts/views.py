import requests
import traceback
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg
from notes.models import Note
from todos.models import Task
from budget.models import Income, Expense
from datetime import date, datetime
import calendar as pycal

def Landing(request):
    return render(request, 'Landing.html')


@login_required
def home(request):
    today = date.today()
    current_date = datetime.now()

    # Generate calendar data
    cal = pycal.Calendar(firstweekday=0)  # Monday first
    month_dates = cal.monthdatescalendar(current_date.year, current_date.month)

    # Get all tasks for calendar
    all_tasks = Task.objects.filter(user=request.user)

    # Prepare calendar days and task days
    calendar_days = []
    task_days = []
    for week in month_dates:
        for day in week:
            if day.month == current_date.month:
                calendar_days.append(day.day)
                # Check if any tasks on this day
                if all_tasks.filter(due_date__day=day.day, due_date__month=current_date.month,
                                    due_date__year=current_date.year).exists():
                    task_days.append(day.day)
            else:
                calendar_days.append(0)

    # Weekday headers
    week_days = ['M', 'T', 'W', 'T', 'F', 'S', 'S']

    # Budget data
    incomes = Income.objects.filter(user=request.user).order_by('-date')[:5]
    expenses = Expense.objects.filter(user=request.user).order_by('-date')[:5]
    total_income = Income.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    # Calculate savings percentage
    if total_income > 0:
        savings_percentage = (balance / total_income) * 100
    else:
        savings_percentage = 0

    # Notes data
    notes = Note.objects.filter(user=request.user).order_by('-created_at')[:5]

    # Todos data
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    completed_count = tasks.filter(is_completed=True).count()
    pending_count = tasks.filter(is_completed=False).count()
    overdue_count = tasks.filter(is_completed=False, due_date__lt=today).count()

    # Productivity score
    if tasks.count() > 0:
        productivity_score = (completed_count / tasks.count()) * 100
    else:
        productivity_score = 0

    # Additional stats
    tasks_this_month = Task.objects.filter(
        user=request.user,
        created_at__month=today.month,
        created_at__year=today.year
    ).count()

    # Average daily spend
    avg_daily_spend_result = Expense.objects.filter(
        user=request.user,
        date__month=today.month,
        date__year=today.year
    ).aggregate(Avg('amount'))
    avg_daily_spend = avg_daily_spend_result['amount__avg'] or 0

    context = {
        # Budget data
        'balance': balance,
        'total_income': total_income,
        'total_expense': total_expense,
        'savings_percentage': savings_percentage,
        'incomes': incomes,
        'expenses': expenses,

        # Notes data
        'notes': notes,

        # Todos data
        'tasks': tasks,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'overdue_count': overdue_count,
        'today': today,

        # Calendar data
        'calendar_days': calendar_days,
        'task_days': task_days,
        'week_days': week_days,
        'current_date': current_date,

        # Additional stats
        'tasks_this_month': tasks_this_month,
        'avg_daily_spend': avg_daily_spend,
        'productivity_score': productivity_score,
    }

    return render(request, 'homepage.html', context)

def register_user(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        user.save()
        messages.success(request, "Account created successfully")
        return redirect('login')

    return render(request, 'accounts/register.html')


# Normal form login with JWT response
def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # Generate JWT
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return JsonResponse({
                "success": True,
                "access_token": access_token,
                "username": user.username
            })
        else:
            return JsonResponse({"success": False, "error": "Invalid credentials"}, status=401)
    return render(request, "accounts/login.html")


# Google JWT endpoint
def google_jwt(request):
    user = request.user
    if user.is_authenticated:
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return JsonResponse({
            "success": True,
            "access_token": access_token,
            "username": user.username
        })
    return JsonResponse({"success": False, "error": "User not authenticated"}, status=401)


def logout_user(request):
    logout(request)
    # messages.success(request, "Logged out successfully")
    return redirect('login')


# for user profile page
@login_required
def profile(request):

    context = {
        'user': request.user,
        'date_joined': request.user.date_joined.strftime('%B %d, %Y'),
        'last_login': request.user.last_login.strftime('%B %d, %Y at %I:%M %p') if request.user.last_login else 'Never',
    }
    return render(request, 'userprofile.html', context)


# user update their username
@login_required
def edit_profile(request):

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        # Update user's name
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('profile')

    return render(request, 'edit_profile.html', {'user': request.user})


