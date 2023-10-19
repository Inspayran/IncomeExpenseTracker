from django.shortcuts import render, redirect
import os
import json
from django.conf import settings
from .models import UserPreferences
from django.contrib import messages
from django.views import View


class Index(View):
    def get(self, request):
        user_preferences, created = self._user_exists(request)

        currency_data = self._load_currency_data()

        context = {'currency_data': currency_data, 'user_preferences': user_preferences}
        return render(request, 'preferences/index.html', context)

    def post(self, request):
        currency = request.POST.get('currency')

        user_preferences, created = self._user_exists(request)

        if user_preferences:
            user_preferences.currency = currency
            user_preferences.save()
        else:
            UserPreferences.objects.create(user=request.user, currency=currency)

        messages.success(request, 'Changes saved.')
        return redirect('preferences')

    def _user_exists(self, request):
        return UserPreferences.objects.get_or_create(user=request.user)

    def _load_currency_data(self):
        currency_data = []

        file_path = os.path.join(settings.BASE_DIR, 'currencies.json')

        with open(file_path, 'r') as file:
            data = json.load(file)

            for k, v in data.items():
                currency_data.append({'name': k, 'value': v})

        return currency_data

