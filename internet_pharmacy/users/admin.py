from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Admin


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'card_type', 'bonus_points', 'is_staff']
    list_filter = ['card_type', 'is_staff', 'email_notifications']
    search_fields = ['username', 'email', 'phone']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Додаткова інформація', {
            'fields': ('phone', 'date_of_birth', 'card_type', 'bonus_points')
        }),
        ('Налаштування сповіщень', {
            'fields': ('email_notifications', 'sms_notifications')
        }),
    )


@admin.register(Admin)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'can_manage_catalog', 'can_view_reports']
    list_filter = ['can_manage_catalog', 'can_view_reports', 'can_manage_orders']
    search_fields = ['user__username', 'user__email']