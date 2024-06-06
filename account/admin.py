# admin.py in your account app

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import Account
from account.forms import CustomAccountUpdateForm, CustomAccountCreationForm

class AccountAdmin(UserAdmin):
    form = CustomAccountUpdateForm  # Form for updating accounts
    add_form = CustomAccountCreationForm  # Custom form for creating accounts

    list_display = ('email', 'username', 'is_admin', 'is_active', 'is_staff')
    search_fields = ('email', 'username')
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ('is_admin', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_admin')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Profile', {'fields': ('profile_photo',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_active', 'is_staff', 'is_admin', 'profile_photo')}
         ),
    )

    ordering = ('email',)

admin.site.register(Account, AccountAdmin)