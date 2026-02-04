from django import forms
from .models import Income, Expense, Category


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['source', 'amount', 'date', 'note']


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'description', 'date']
    def __init__(self,*args,**kwargs):
        user= kwargs.pop('user',None)
        super(). __init__(*args,**kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']

        qs = Category.objects.filter(
            name__iexact=name,
            user=self.user
        )

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)  # ✅ exclude self

        if qs.exists():
            raise forms.ValidationError("This category already exists.")

        return name
