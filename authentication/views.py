import json

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect

from authentication.forms import CustomUserCreationForm, LoginForm

from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import authenticate

from authentication.mailings import send_activation_email, send_reset_password_email
from .utils import account_activation_token


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_error': 'Username should only contain alphanumeric characters'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'Sorry username is use, choose another one'}, status=409)

        return JsonResponse({'username_valid': True})


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']

        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'Sorry email is use, choose another one'}, status=409)

        return JsonResponse({'email_valid': True})


class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')

        field_values = {
            'username': username,
            'email': email,
        }

        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            send_activation_email(request, user)

            messages.success(request, 'Account successfully created.')
            return redirect('register')
        else:
            self._handle_form_errors(request, form)

        return render(request, 'authentication/register.html', {'field_values': field_values})

    def _handle_form_errors(self, request, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f'Error in field {field}: {error}')


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('login' + '?message=' + 'User already activated.')

            if user.is_active:
                messages.info(request, 'Account is already activated. You can now log in.')
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully.')
            return redirect('login')

        except Exception as e:
            pass
        return redirect('login')


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'authentication/login.html')

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                messages.success(request, 'You have been successfully logged in.')
                return redirect('/')
            else:
                messages.error(request, 'Invalid username or password.')

        return render(request, 'authentication/login.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
            messages.success(request, 'You have been logged out.')
            return redirect('login')


class ResetPassword(View):
    def get(self, request):
        context = {
            'values': request.POST,
        }

        return render(request, 'authentication/reset_password.html', context)

    def post(self, request):

        email = request.POST.get('email')

        context = {
            'values': request.POST,
        }

        if not validate_email(email):
            messages.error(request, 'Please supply a valid email.')
            return render(request, 'authentication/reset_password.html', context)

        send_reset_password_email(request)
        messages.success(request, 'Сообщение было отправлено')

        return render(request, 'authentication/reset_password.html')


class CompleteResetPassword(View):

    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }

        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
        if not PasswordResetTokenGenerator().check_token(user, token):
            messages.info(request, 'Password link is invalid, please request a new one.')
            return render(request, 'authentication/reset_password.html', context)
        return render(request, 'authentication/reset_password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }

        password = request.POST.get('password1')
        confirm_password = request.POST.get('password2')

        if password != confirm_password:
            messages.error(request, 'Password do not match.')
            return render(request, 'authentication/set_password.html', context)

        user_id = force_str(urlsafe_base64_decode(uidb64))

        user = User.objects.get(pk=user_id)
        user.set_password(password)
        user.save()

        messages.success(request, 'Password reset successfully.')
        return redirect('login')

