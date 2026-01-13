# from django.contrib import admin
# from .models import Order, OrderItem, ShoppingCart, CartItem
#
#
# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     extra = 0
#     readonly_fields = ['get_total_price']
#
#
# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ['id', 'user', 'order_type', 'status', 'total_price', 'is_paid', 'created_at']
#     list_filter = ['order_type', 'status', 'is_paid', 'created_at']
#     search_fields = ['user__username', 'user__email']
#     readonly_fields = ['subtotal', 'discount_amount', 'total_price', 'created_at', 'updated_at']
#     inlines = [OrderItemInline]
#
#     fieldsets = (
#         ('Основна інформація', {
#             'fields': ('user', 'order_type', 'status', 'pharmacy')
#         }),
#         ('Ціни', {
#             'fields': ('subtotal', 'discount_amount', 'delivery_cost', 'total_price')
#         }),
#         ('Доставка', {
#             'fields': ('delivery_address', 'delivery_time')
#         }),
#         ('Оплата', {
#             'fields': ('payment_method', 'is_paid')
#         }),
#         ('Додатково', {
#             'fields': ('comment', 'created_at', 'updated_at')
#         }),
#     )
#
#
# class CartItemInline(admin.TabularInline):
#     model = CartItem
#     extra = 0
#
#
# @admin.register(ShoppingCart)
# class ShoppingCartAdmin(admin.ModelAdmin):
#     list_display = ['user', 'get_items_count', 'get_total_price', 'updated_at']
#     search_fields = ['user__username']
#     inlines = [CartItemInline]
#
#     def get_items_count(self, obj):
#         return obj.get_items_count()
#
#     get_items_count.short_description = 'Товарів'
from django.contrib import admin
from .models import Order, OrderItem, ShoppingCart, CartItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Змінили з 0 на 1
    fields = ['medication', 'quantity', 'price']  # Додали поле price
    readonly_fields = []  # Прибрали readonly для price

    def get_total_price(self, obj):
        if obj.id:
            return obj.get_total_price()
        return 0

    get_total_price.short_description = 'Сума'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'order_type', 'status', 'total_price', 'is_paid', 'created_at']
    list_filter = ['order_type', 'status', 'is_paid', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']  # Прибрали автообчислювані поля
    inlines = [OrderItemInline]

    fieldsets = (
        ('Основна інформація', {
            'fields': ('user', 'order_type', 'status', 'pharmacy')
        }),
        ('Ціни', {
            'fields': ('subtotal', 'discount_amount', 'delivery_cost', 'total_price')
        }),
        ('Доставка', {
            'fields': ('delivery_address', 'delivery_time')
        }),
        ('Оплата', {
            'fields': ('payment_method', 'is_paid')
        }),
        ('Додатково', {
            'fields': ('comment', 'created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        """Перераховуємо суму при збереженні"""
        super().save_model(request, obj, form, change)
        if obj.id:
            obj.calculate_total()


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'medication', 'quantity', 'price', 'get_total']
    list_filter = ['order__status']
    search_fields = ['medication__name', 'order__id']

    def get_total(self, obj):
        return obj.get_total_price()

    get_total.short_description = 'Сума'


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_items_count', 'get_total_price', 'updated_at']
    search_fields = ['user__username']
    inlines = [CartItemInline]

    def get_items_count(self, obj):
        return obj.get_items_count()

    get_items_count.short_description = 'Товарів'