from django.urls import path
from .views import Index

urlpatterns = [
    path('preferences', Index.as_view(), name='preferences'),
]