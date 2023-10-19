import os

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse

from authentication.utils import account_activation_token
from django.core.mail import EmailMessage

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import User
import threading


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)


def send_activation_email(request, user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)

    domain = get_current_site(request).domain
    link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token})

    activate_url = f'http://{domain}{link}'

    email_subject = 'Activate your account.'
    email_body = f'Hi {user.username}! \nPlease use this link to verify your account.\n' \
                 f'{activate_url}'

    email = EmailMessage(
        email_subject,
        email_body,
        os.environ.get('EMAIL_HOST_USER'),
        [user.email],
    )
    EmailThread(email).start()


def send_reset_password_email(request):
    email = request.POST.get('email')
    user = User.objects.get(email=email)

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = PasswordResetTokenGenerator().make_token(user)

    domain = get_current_site(request).domain

    link = reverse('set-password', kwargs={'uidb64': uidb64, 'token': token})

    reset_url = f'http://{domain}{link}'

    email_subject = 'Password reset Instruction'
    email_body = f'Hi {user.username}! \n Please user this link to reset your password.\n ' \
                 f'{reset_url}'

    email = EmailMessage(
        email_subject,
        email_body,
        os.environ.get('EMAIL_HOST_USER'),
        [email],
    )
    EmailThread(email).start()
