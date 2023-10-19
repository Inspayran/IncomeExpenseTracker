import datetime

from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from user_preferences.models import UserPreferences
from .models import Category, Expense
from django.views import View
from django.contrib import messages
from .forms import ExpenseForm
from django.core.paginator import Paginator
import json
from django.http import JsonResponse


@login_required(login_url='login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)

    paginator = Paginator(expenses, 4)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)

    currency = UserPreferences.objects.get(user=request.user).currency

    context = {
        'expenses': expenses,
        'categories': categories,
        'values': request.POST,
        'page_obj': page_obj,
        'currency': currency,
    }
    return render(request, 'expenses/index.html', context)


def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')

        expenses = Expense.objects.filter(
            Q(amount__istartswith=search_str) |
            Q(date__istartswith=search_str) |
            Q(description__icontains=search_str) |
            Q(category__icontains=search_str),
            owner=request.user
        )
        data = expenses.values()

        return JsonResponse(list(data), safe=False)


@method_decorator(login_required(login_url='login'), name='dispatch')
class AddExpense(View):
    def get(self, request):
        categories = Category.objects.all()
        context = {
            'categories': categories,
        }

        return render(request, 'expenses/add_expense.html', context)

    def post(self, request):
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('date')
        category = request.POST.get('category')

        if not amount:
            messages.error(request, 'Amount is required.')
        if not description:
            messages.error(request, 'Description is required.')

        context = {
            'values': request.POST,
        }

        Expense.objects.create(amount=amount, date=date, category=category, description=description, owner=request.user)
        messages.success(request, 'Expense saved successfully.')

        return render(request, 'expenses/add_expense.html', context)


class ExpenseEdit(View):
    def get(self, request, pk):
        expense = Expense.objects.get(pk=pk)
        form = ExpenseForm(instance=expense)
        categories = Category.objects.all()
        context = {
            'expense': expense,
            'categories': categories,
            'form': form,
        }

        return render(request, 'expenses/edit_expense.html', context)

    def post(self, request, pk):
        expense = Expense.objects.get(pk=pk)
        categories = Category.objects.all()
        form = ExpenseForm(request.POST, instance=expense)

        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully.')
            return redirect('expenses')

        context = {
            'expense': expense,
            'categories': categories,
            'form': form,
        }
        return render(request, 'expenses/edit_expense.html', context)


def delete_expense(request, pk):
    expense = Expense.objects.get(pk=pk)
    expense.delete()

    messages.success(request, 'Expense deleted successfully.')

    return redirect('expenses')


def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    expenses = Expense.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}

    def get_category(expense):
        return expense.category

    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount

        return amount

    for i in expenses:
        for j in category_list:
            finalrep[j] = get_expense_category_amount(j)

    return JsonResponse({'expense_category_data': finalrep}, safe=False)


def stats_view(request):
    return render(request, 'expenses/stats.html')


