from django.contrib import admin

from budget.models import Category, Expense, Income

# Register your models here.
admin.site.register(Category)
admin.site.register(Expense)
admin.site.register(Income)
