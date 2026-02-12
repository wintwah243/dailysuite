from django.utils import timezone
from datetime import datetime, timedelta
from .models import Income, Expense, Category
from django.db.models import Sum, Q
from decimal import Decimal
import re


class BudgetCommandHandler:
    def __init__(self, user):
        self.user = user

    def add_income(self, amount, source, date=None, note=""):
        """Add a new income entry"""
        if date is None:
            date = timezone.now().date()

        income = Income.objects.create(
            user=self.user,
            amount=Decimal(str(amount)),
            source=source,
            date=date,
            note=note
        )
        return {
            "success": True,
            "message": f"Added income successfully: {source} - {amount}Ks",
            "income": income
        }

    def add_expense(self, amount, description, category_name=None, date=None):
        """Add a new expense entry"""
        if date is None:
            date = timezone.now().date()

        category = None
        if category_name:
            # Try to find category by name
            try:
                category = Category.objects.get(
                    user=self.user,
                    name__icontains=category_name
                )
            except Category.DoesNotExist:
                # Create new category if it doesn't exist
                category = Category.objects.create(
                    user=self.user,
                    name=category_name.capitalize()
                )
            except Category.MultipleObjectsReturned:
                category = Category.objects.filter(
                    user=self.user,
                    name__icontains=category_name
                ).first()

        expense = Expense.objects.create(
            user=self.user,
            amount=Decimal(str(amount)),
            description=description,
            category=category,
            date=date
        )

        category_text = f" in {category.name}" if category else ""
        return {
            "success": True,
            "message": f"Added expense successfully: {description}{category_text} - {amount}Ks",
            "expense": expense
        }

    def delete_income(self, identifier):
        """Delete income by ID or source"""
        # Try by ID first
        if str(identifier).isdigit():
            try:
                income = Income.objects.get(id=identifier, user=self.user)
                income_source = income.source
                income.delete()
                return {"success": True, "message": f"Deleted income successfully: '{income_source}'"}
            except Income.DoesNotExist:
                pass

        # Try by source name
        incomes = Income.objects.filter(
            user=self.user,
            source__icontains=identifier
        )

        if not incomes.exists():
            return {"success": False, "message": f"No income found matching '{identifier}'"}

        if incomes.count() > 1:
            income_list = "\n".join([f"  • ID {i.id}: '{i.source}' - {i.amount}Ks ({i.date})" for i in incomes[:5]])
            return {
                "success": False,
                "message": f"Multiple incomes found. Please use ID:\n{income_list}"
            }

        income = incomes.first()
        income_source = income.source
        income.delete()
        return {"success": True, "message": f"Deleted income successfully: '{income_source}'"}

    def delete_expense(self, identifier):
        """Delete expense by ID or description"""
        # Try by ID first
        if str(identifier).isdigit():
            try:
                expense = Expense.objects.get(id=identifier, user=self.user)
                expense_desc = expense.description
                expense.delete()
                return {"success": True, "message": f"Deleted expense successfully: '{expense_desc}'"}
            except Expense.DoesNotExist:
                pass

        # Try by description
        expenses = Expense.objects.filter(
            user=self.user,
            description__icontains=identifier
        )

        if not expenses.exists():
            return {"success": False, "message": f"No expense found matching '{identifier}'"}

        if expenses.count() > 1:
            expense_list = "\n".join(
                [f"  • ID {e.id}: '{e.description}' - {e.amount}Ks ({e.date})" for e in expenses[:5]])
            return {
                "success": False,
                "message": f"Multiple expenses found. Please use ID:\n{expense_list}"
            }

        expense = expenses.first()
        expense_desc = expense.description
        expense.delete()
        return {"success": True, "message": f"Deleted expense successfully: '{expense_desc}'"}

    def delete_last_transaction(self, transaction_type=None):
        """Delete the most recent transaction"""
        if transaction_type == 'income':
            last = Income.objects.filter(user=self.user).order_by('-date', '-id').first()
            if last:
                last_source = last.source
                last_amount = last.amount
                last.delete()
                return {"success": True, "message": f"Deleted last income successfully: '{last_source}' - {last_amount}Ks"}
            return {"success": False, "message": "No income transactions found"}

        elif transaction_type == 'expense':
            last = Expense.objects.filter(user=self.user).order_by('-date', '-id').first()
            if last:
                last_desc = last.description
                last_amount = last.amount
                last.delete()
                return {"success": True, "message": f"Deleted last expense successfully: '{last_desc}' - {last_amount}Ks"}
            return {"success": False, "message": "No expense transactions found"}

        else:
            # Try expense first, then income
            last_expense = Expense.objects.filter(user=self.user).order_by('-date', '-id').first()
            last_income = Income.objects.filter(user=self.user).order_by('-date', '-id').first()

            if last_expense and last_income:
                if last_expense.date >= last_income.date:
                    last_desc = last_expense.description
                    last_amount = last_expense.amount
                    last_expense.delete()
                    return {"success": True, "message": f"Deleted last expense successfully: '{last_desc}' - {last_amount}Ks"}
                else:
                    last_source = last_income.source
                    last_amount = last_income.amount
                    last_income.delete()
                    return {"success": True, "message": f"Deleted last income successfully: '{last_source}' - {last_amount}Ks"}
            elif last_expense:
                last_desc = last_expense.description
                last_amount = last_expense.amount
                last_expense.delete()
                return {"success": True, "message": f"Deleted last expense successfully: '{last_desc}' - {last_amount}Ks"}
            elif last_income:
                last_source = last_income.source
                last_amount = last_income.amount
                last_income.delete()
                return {"success": True, "message": f"Deleted last income successfully: '{last_source}' - {last_amount}Ks"}
            else:
                return {"success": False, "message": "No transactions found"}

    def get_summary(self, period=None):
        """Get budget summary"""
        today = timezone.now().date()

        # Date filtering
        if period == 'today':
            date_filter = Q(date=today)
            period_text = "today"
        elif period == 'week':
            week_start = today - timedelta(days=today.weekday())
            date_filter = Q(date__gte=week_start)
            period_text = "this week"
        elif period == 'month':
            date_filter = Q(date__year=today.year, date__month=today.month)
            period_text = "this month"
        elif period == 'year':
            date_filter = Q(date__year=today.year)
            period_text = "this year"
        else:
            date_filter = Q()
            period_text = "all time"

        # Calculate totals
        incomes = Income.objects.filter(user=self.user).filter(date_filter)
        expenses = Expense.objects.filter(user=self.user).filter(date_filter)

        total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        balance = total_income - total_expense

        # Get top categories
        category_spending = {}
        for expense in expenses:
            cat_name = expense.category.name if expense.category else "Uncategorized"
            category_spending[cat_name] = category_spending.get(cat_name, 0) + expense.amount

        top_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:3]
        top_cats_text = "\n".join([f"  • {cat}: {amount}Ks" for cat, amount in top_categories])

        message = f"Budget Summary {period_text}:\n"
        message += f"Total Income: {total_income}Ks\n"
        message += f"Total Expense: {total_expense}Ks\n"
        message += f"Total Balance: {balance}Ks\n"

        if top_cats_text:
            message += f"\nTop Categories:\n{top_cats_text}"

        # Savings rate
        if total_income > 0:
            savings_rate = (balance / total_income) * 100
            message += f"\n\nSavings Rate: {savings_rate:.1f}%"

        return {
            "success": True,
            "message": message,
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance
        }

    def get_category_spending(self, category_name):
        """Get spending for a specific category"""
        try:
            category = Category.objects.get(
                user=self.user,
                name__icontains=category_name
            )
        except Category.DoesNotExist:
            return {"success": False, "message": f"Category '{category_name}' not found"}
        except Category.MultipleObjectsReturned:
            category = Category.objects.filter(
                user=self.user,
                name__icontains=category_name
            ).first()

        expenses = Expense.objects.filter(
            user=self.user,
            category=category
        )

        total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        count = expenses.count()

        # Get recent expenses
        recent = expenses.order_by('-date')[:3]
        recent_text = "\n".join([f"  • {e.date}: {e.description} - {e.amount}Ks" for e in recent])

        message = f" Spending in '{category.name}':\n"
        message += f"  Total: {total}Ks\n"
        message += f"  Transactions: {count}\n"
        if recent_text:
            message += f"\nRecent:\n{recent_text}"

        return {
            "success": True,
            "message": message,
            "category": category.name,
            "total": total,
            "count": count
        }

    def list_transactions(self, limit=5, transaction_type=None):
        """List recent transactions"""
        message = "Recent Transactions:\n\n"
        has_transactions = False

        if transaction_type in [None, 'income']:
            incomes = Income.objects.filter(user=self.user).order_by('-date', '-id')[:limit]
            if incomes.exists():
                has_transactions = True
                message += "Income:\n"
                for inc in incomes:
                    message += f"  • {inc.date}: {inc.source} - {inc.amount}Ks (ID: {inc.id})\n"
                message += "\n"

        if transaction_type in [None, 'expense']:
            expenses = Expense.objects.filter(user=self.user).order_by('-date', '-id')[:limit]
            if expenses.exists():
                has_transactions = True
                message += "Expense:\n"
                for exp in expenses:
                    cat = f"[{exp.category.name}]" if exp.category else "[Uncategorized]"
                    message += f"  • {exp.date}: {cat} {exp.description} - {exp.amount}Ks (ID: {exp.id})\n"

        if not has_transactions:
            if transaction_type == 'income':
                return {"success": True, "message": "No income transactions found"}
            elif transaction_type == 'expense':
                return {"success": True, "message": "No expense transactions found"}
            else:
                return {"success": True, "message": "No transactions found"}

        return {"success": True, "message": message}

    def parse_date(self, date_string):
        """Parse natural language date strings"""
        if not date_string:
            return timezone.now().date()

        today = timezone.now().date()
        date_string = date_string.lower().strip()

        if date_string in ['today', 'now']:
            return today
        elif date_string == 'yesterday':
            return today - timedelta(days=1)
        elif date_string == 'tomorrow':
            return today + timedelta(days=1)
        elif 'day' in date_string and any(char.isdigit() for char in date_string):
            match = re.search(r'in\s+(\d+)\s+days?', date_string)
            if match:
                days = int(match.group(1))
                return today + timedelta(days=days)

        try:
            return datetime.strptime(date_string, '%Y-%m-%d').date()
        except:
            pass

        try:
            return datetime.strptime(date_string, '%d/%m/%Y').date()
        except:
            pass

        return today