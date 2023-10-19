from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


UserAdmin.list_display += ('username', 'email', 'is_active', 'password',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
