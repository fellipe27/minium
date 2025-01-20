from django.contrib.auth.admin import UserAdmin
from .models import User
from django.contrib import admin

class UserAdm(UserAdmin):
    model = User
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, { 'fields': ('email', 'birthday') }),
    )
    fieldsets = (
        (None, {
            'fields': ('id', 'username', 'email', 'birthday', 'bio', 'interests', 'following')
        }),
        ('Important dates', { 'fields': ('last_login', 'date_joined') })
    )
    readonly_fields = ('id',)

admin.site.register(User, UserAdm)
