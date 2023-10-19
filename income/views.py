import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View

from user_preferences.models import UserPreferences
from .forms import IncomeForm
from .models import Source, Income


@login_required(login_url='login')
def index(request):
    sources = Source.objects.all()
    income = Income.objects.filter(owner=request.user)

    paginator = Paginator(income, 4)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)

    currency = UserPreferences.objects.get(user=request.user).currency

    context = {
        'income': income,
        'sources': sources,
        'values': request.POST,
        'page_obj': page_obj,
        'currency': currency,
    }
    return render(request, 'income/index.html', context)


def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')

        income = Income.objects.filter(
            Q(amount__is_startswith=search_str) |
            Q(description__is_startswith=search_str) |
            Q(date__is_startswith=search_str) |
            Q(source__is_startswith=search_str),
            owner=request.user
        )

        data = income.values()

        return JsonResponse(list(data), safe=False)


@method_decorator(login_required(login_url='login'), name='dispatch')
class AddIncome(View):
    def get(self, request):
        sources = Source.objects.all()
        context = {
            'sources': sources,
        }

        return render(request, 'income/add_income.html', context)

    def post(self, request):
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('date')
        source = request.POST.get('source')

        if not amount:
            messages.error(request, 'Amount is required.')
        if not description:
            messages.error(request, 'Description is required.')

        context = {
            'values': request.POST,
        }

        Income.objects.create(amount=amount, date=date, source=source, description=description, owner=request.user)
        messages.success(request, 'Record saved successfully.')

        return render(request, 'income/add_income.html', context)


class EditIncome(View):
    def get(self, request, pk):
        income = Income.objects.get(pk=pk)
        form = IncomeForm(instance=income)
        sources = Source.objects.all()
        context = {
            'income': income,
            'sources': sources,
            'form': form,
        }

        return render(request, 'income/edit_income.html', context)

    def post(self, request, pk):
        income = Income.objects.get(pk=pk)
        source = Source.objects.all()
        form = IncomeForm(request.POST, instance=income)

        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully.')
            return redirect('income')

        context = {
            'income': income,
            'source': source,
            'form': form,
        }
        return render(request, 'income/income.html', context)


def delete_income(request, pk):
    income = Income.objects.get(pk=pk)
    income.delete()

    messages.success(request, 'Income deleted successfully.')

    return redirect('income')
