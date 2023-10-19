from django.contrib.auth.models import User
from django.db import models


class UserPreferences(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return str(self.user) + 's ' + 'preferences'
