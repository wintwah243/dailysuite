from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .ai_command_parser import parse_budget_command
from .command_handlers import BudgetCommandHandler
from .models import Income, Expense, Category


@login_required
@require_POST
@csrf_exempt
def budget_chat_command(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({
                'success': False,
                'message': 'Please enter a command'
            })

        # Parse command using Groq AI
        command_data = parse_budget_command(user_message, request.user.username)
        action = command_data.get('action', 'unknown')

        # Initialize command handler
        handler = BudgetCommandHandler(request.user)

        # Execute command based on action
        if action == 'add_income':
            result = handler.add_income(
                amount=command_data.get('amount', 0),
                source=command_data.get('source', 'Unknown'),
                date=handler.parse_date(command_data.get('date')),
                note=command_data.get('note', '')
            )

        elif action == 'add_expense':
            result = handler.add_expense(
                amount=command_data.get('amount', 0),
                description=command_data.get('description', 'Unknown'),
                category_name=command_data.get('category'),
                date=handler.parse_date(command_data.get('date'))
            )

        elif action == 'delete_income':
            result = handler.delete_income(command_data.get('identifier', ''))

        elif action == 'delete_expense':
            result = handler.delete_expense(command_data.get('identifier', ''))

        elif action == 'delete_last':
            result = handler.delete_last_transaction(command_data.get('transaction_type'))

        elif action == 'summary':
            result = handler.get_summary(command_data.get('period'))

        elif action == 'category_spending':
            result = handler.get_category_spending(command_data.get('category', ''))

        elif action == 'list':
            limit = int(command_data.get('limit', 5))
            result = handler.list_transactions(
                limit=limit,
                transaction_type=command_data.get('transaction_type')
            )

        else:
            # for Unknown command
            result = {
                'success': False,
                'message': "I didn't understand that. Try commands like:\n"
                           "• 'add income 3000 salary'\n"
                           "• 'add expense 25.50 for lunch food'\n"
                           "• 'show my budget summary'\n"
                           "• 'how much did I spend on food'\n"
                           "• 'delete expense 5'\n"
                           "• 'delete last expense'\n"
                           "• 'show my expenses'"
            }

        return JsonResponse({
            'success': result.get('success', False),
            'message': result.get('message', ''),
            'action': action,
            'data': result
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
def get_budget_data_json(request):
    """Return budget data as JSON for the chatbot UI"""
    incomes = Income.objects.filter(user=request.user).order_by('-date', '-id')[:10]
    expenses = Expense.objects.filter(user=request.user).order_by('-date', '-id')[:10]

    income_data = []
    for income in incomes:
        income_data.append({
            'id': income.id,
            'source': income.source,
            'amount': float(income.amount),
            'date': income.date.isoformat(),
            'note': income.note
        })

    expense_data = []
    for expense in expenses:
        expense_data.append({
            'id': expense.id,
            'description': expense.description,
            'amount': float(expense.amount),
            'date': expense.date.isoformat(),
            'category': expense.category.name if expense.category else None,
            'category_id': expense.category.id if expense.category else None
        })

    # Get summary
    from django.db.models import Sum
    total_income = Income.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0

    return JsonResponse({
        'incomes': income_data,
        'expenses': expense_data,
        'total_income': float(total_income),
        'total_expense': float(total_expense),
        'balance': float(total_income - total_expense)
    })