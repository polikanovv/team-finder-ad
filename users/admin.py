from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = ['email', 'name', 'surname', 'is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональные данные', {'fields': ('name', 'surname', 'avatar', 'phone', 'github_url', 'about')}),
        ('Права', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'surname', 'password1', 'password2'),
        }),
    )
    filter_horizontal = ['groups', 'user_permissions', 'skills']
