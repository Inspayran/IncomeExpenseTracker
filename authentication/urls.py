from .views import RegistrationView, UsernameValidationView, \
    EmailValidationView, VerificationView, LoginView, LogoutView, ResetPassword, CompleteResetPassword
from django.urls import path
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('register', RegistrationView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name='activate'),

    path('validate-username', csrf_exempt(UsernameValidationView.as_view()), name='validate-username'),
    path('validate-email', csrf_exempt(EmailValidationView.as_view()), name='validate-email'),

    path('request-password/', ResetPassword.as_view(), name='request-password'),
    path('set-password/<uidb64>/<token>', CompleteResetPassword.as_view(), name='set-password'),
]
