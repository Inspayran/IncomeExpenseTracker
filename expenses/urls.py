from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt
from .downloads import csv_views, excel_views, pdf_views


urlpatterns = [
    path('', views.index, name='expenses'),
    path('add-expenses', views.AddExpense.as_view(), name='add-expenses'),
    path('edit-expenses/<int:pk>', views.ExpenseEdit.as_view(), name='edit-expenses'),
    path('delete-expense/<int:pk>', views.delete_expense, name='delete-expense'),
    path('search-expenses', csrf_exempt(views.search_expenses), name='search-expenses'),

    path('stats', views.stats_view, name='stats'),
    path('expense-category-summary', views.expense_category_summary, name='expense_category_summary'),

    path('export-csv', csv_views.export_csv, name='export-csv'),
    path('export-excel', excel_views.export_excel, name='export-excel'),
    path('export-pdf', pdf_views.export_pdf, name='export-pdf'),
]
