from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from .models import Income, Expense, Category
from .forms import IncomeForm, ExpenseForm, CategoryForm


@login_required
def dashboard(request):
    incomes = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)

    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    categories = Category.objects.filter(user=request.user)

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'incomes': incomes,
        'expenses': expenses,
        'categories': categories,
    }

    return render(request, 'budget/budget_home.html', context)

@login_required
def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            return redirect('dashboard')
    else:
        form = IncomeForm()

    return render(request, 'budget/add_income.html', {'form': form})

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST,user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm(user=request.user)

    return render(request, 'budget/add_expense.html', {'form': form})

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, user=request.user)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('add_expense')
    else:
        form = CategoryForm(user=request.user)

    return render(request, 'budget/add_category.html', {'form': form})

@login_required
def update_income(request, pk):
    income = Income.objects.get(id=pk, user=request.user)

    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = IncomeForm(instance=income)

    return render(request, 'budget/update_income.html', {'form': form})

@login_required
def update_expense(request, pk):
    expense = Expense.objects.get(id=pk, user=request.user)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm(instance=expense, user=request.user)

    return render(request, 'budget/update_expense.html', {'form': form})

@login_required
def update_category(request, pk):
    category = Category.objects.get(id=pk, user=request.user)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category,user=request.user)
        if form.is_valid():
            form.save()
            return redirect('add_expense')
    else:
        form = CategoryForm(instance=category,user=request.user)

    return render(request, 'budget/update_category.html', {'form': form})

@login_required
def delete_income(request, pk):
    income = Income.objects.get(id=pk, user=request.user)
    income.delete()
    return redirect('dashboard')

@login_required
def delete_expense(request, pk):
    expense = Expense.objects.get(id=pk, user=request.user)
    expense.delete()
    return redirect('dashboard')

@login_required
def delete_category(request, pk):
    category = Category.objects.get(id=pk, user=request.user)
    category.delete()
    return redirect('dashboard')



