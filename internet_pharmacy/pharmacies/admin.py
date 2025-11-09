from django.contrib import admin
from .models import Pharmacy, PharmacyStock


@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'address', 'phone', 'is_active']
    list_filter = ['city', 'is_active']
    search_fields = ['name', 'address', 'phone']
    list_editable = ['is_active']


@admin.register(PharmacyStock)
class PharmacyStockAdmin(admin.ModelAdmin):
    list_display = ['pharmacy', 'medication', 'quantity', 'last_updated']
    list_filter = ['pharmacy', 'last_updated']
    search_fields = ['pharmacy__name', 'medication__name']
    list_editable = ['quantity']