from django.contrib.auth.admin import UserAdmin
from .models import User
from django.contrib import admin

class UserAdm(UserAdmin):
    model = User
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, { 'fields': ('email', 'birthday') }),
    )
    fieldsets = (
        ('Personal Info', { 'fields': ('id', 'username', 'email', 'birthday', 'bio') }),
        ('Permissions', { 'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions') }),
        ('Important dates', { 'fields': ('last_login', 'date_joined') })
    )
    readonly_fields = ('id',)

admin.site.register(User, UserAdm)
