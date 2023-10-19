from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('income', views.index, name='income'),
    path('add-income', views.AddIncome.as_view(), name='add-income'),
    path('edit-income/<int:pk>', views.EditIncome.as_view(), name='edit-income'),
    path('delete-income/<int:pk>', views.delete_income, name='delete-income'),
    path('search-income', csrf_exempt(views.search_income), name='search-income')
]