from django.contrib import admin
from account.models import UserAccount
from django.contrib.auth.admin import UserAdmin


class AccountConfig(UserAdmin):
    model = UserAccount
    search_fields = ('email', 'user_name', )
    list_filter = ('email', 'user_name', 'is_active', 'is_staff')
    ordering = ('email',)
    list_display = ('email', 'id', 'user_name', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'user_name', )}),
        ('Permissions', {'fields': ('is_active', 'is_staff')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'user_name', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser')}
         ),
    )


admin.site.register(UserAccount, AccountConfig)