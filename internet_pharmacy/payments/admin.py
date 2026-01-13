from django.contrib import admin
from .models import Payment, Delivery


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount', 'payment_method', 'status', 'created_at']
    list_filter = ['payment_method', 'status', 'created_at']
    search_fields = ['order__user__username', 'transaction_id']
    readonly_fields = ['created_at', 'paid_at']


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'delivery_method', 'status', 'delivery_cost', 'created_at']
    list_filter = ['delivery_method', 'status', 'created_at']
    search_fields = ['order__user__username']
    readonly_fields = ['created_at', 'delivered_at']