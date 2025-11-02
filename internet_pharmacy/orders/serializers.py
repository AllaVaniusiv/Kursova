from rest_framework import serializers
from .models import Order, OrderItem, ShoppingCart, CartItem
from medications.serializers import MedicationListSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Серіалізатор для товару в замовленні"""

    medication_name = serializers.CharField(source='medication.name', read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'medication', 'medication_name', 'quantity', 'price', 'total_price']
        read_only_fields = ['price']

    def get_total_price(self, obj):
        return obj.get_total_price()


class OrderSerializer(serializers.ModelSerializer):
    """Серіалізатор для замовлення"""

    items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    pharmacy_name = serializers.CharField(source='pharmacy.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_type_display = serializers.CharField(source='get_order_type_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_name', 'order_type', 'order_type_display',
            'status', 'status_display', 'pharmacy', 'pharmacy_name',
            'subtotal', 'discount_amount', 'delivery_cost', 'total_price',
            'delivery_address', 'delivery_time', 'payment_method',
            'is_paid', 'comment', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'user', 'subtotal', 'discount_amount', 'total_price',
            'created_at', 'updated_at'
        ]


class OrderCreateSerializer(serializers.Serializer):
    """Серіалізатор для створення замовлення через Builder"""

    order_type = serializers.ChoiceField(choices=['delivery', 'pickup'])
    pharmacy_id = serializers.IntegerField(required=False, allow_null=True)
    items = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()),
        write_only=True
    )
    delivery_address = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.CharField(required=False, allow_blank=True)
    comment = serializers.CharField(required=False, allow_blank=True)

    def validate_items(self, value):
        """Валідація товарів"""
        if not value:
            raise serializers.ValidationError("Замовлення не може бути порожнім")

        for item in value:
            if 'medication_id' not in item or 'quantity' not in item:
                raise serializers.ValidationError(
                    "Кожен товар має містити medication_id та quantity"
                )
            if item['quantity'] < 1:
                raise serializers.ValidationError("Кількість має бути більше 0")

        return value

    def validate(self, data):
        """Валідація всього замовлення"""
        if data['order_type'] == 'pickup' and not data.get('pharmacy_id'):
            raise serializers.ValidationError(
                "Для самовивозу потрібно вказати аптеку"
            )
        return data


class CartItemSerializer(serializers.ModelSerializer):
    """Серіалізатор для товару в кошику"""

    medication = MedicationListSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'medication', 'quantity', 'total_price', 'added_at']

    def get_total_price(self, obj):
        return obj.get_total_price()


class CartItemAddSerializer(serializers.Serializer):
    """Серіалізатор для додавання товару в кошик"""

    medication_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Серіалізатор для кошика"""

    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = ['id', 'user', 'items', 'total_price', 'items_count', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_total_price(self, obj):
        return obj.get_total_price()

    def get_items_count(self, obj):
        return obj.get_items_count()


class CheckoutSerializer(serializers.Serializer):
    """Серіалізатор для оформлення замовлення з кошика"""

    order_type = serializers.ChoiceField(choices=['delivery', 'pickup'])
    pharmacy_id = serializers.IntegerField(required=False, allow_null=True)
    delivery_address = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data['order_type'] == 'pickup' and not data.get('pharmacy_id'):
            raise serializers.ValidationError(
                "Для самовивозу потрібно вказати аптеку"
            )
        return data