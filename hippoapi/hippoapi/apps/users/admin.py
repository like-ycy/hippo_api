from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class UserModelAdmin(UserAdmin):
    list_display = ["id", "username", "avatar", "mobile"]
    ordering = ('id',)


admin.site.register(User, UserModelAdmin)
