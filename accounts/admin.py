from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin

class UserAdm(UserAdmin):
    model = User
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, { 'fields': ('email', 'birthday') }),
    )
    fieldsets = (
        (None, {
            'fields': ('id', 'username', 'email', 'birthday', 'bio')
        }),
        ('Important dates', { 'fields': ('last_login', 'date_joined') })
    )
    readonly_fields = ('id',)

admin.site.register(User, UserAdm)
