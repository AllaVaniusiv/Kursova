from rest_framework import serializers
from .models import User, Admin


class UserSerializer(serializers.ModelSerializer):
    """Серіалізатор для користувача"""

    card_type_display = serializers.CharField(source='get_card_type_display', read_only=True)
    discount = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'date_of_birth', 'card_type', 'card_type_display',
            'bonus_points', 'discount', 'email_notifications',
            'sms_notifications', 'created_at'
        ]
        read_only_fields = ['bonus_points', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_discount(self, obj):
        """Повертає знижку користувача"""
        return obj.get_discount()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Серіалізатор для реєстрації користувача"""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone'
        ]

    def validate(self, data):
        """Валідація паролів"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Паролі не співпадають")
        return data

    def create(self, validated_data):
        """Створення користувача"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Створюємо кошик для користувача
        from orders.models import ShoppingCart
        ShoppingCart.objects.create(user=user)

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Серіалізатор для профілю користувача"""

    card_type_display = serializers.CharField(source='get_card_type_display', read_only=True)
    discount = serializers.SerializerMethodField()
    orders_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'date_of_birth', 'card_type', 'card_type_display',
            'bonus_points', 'discount', 'email_notifications',
            'sms_notifications', 'orders_count', 'created_at'
        ]
        read_only_fields = ['username', 'bonus_points', 'card_type', 'created_at']

    def get_discount(self, obj):
        return obj.get_discount()

    def get_orders_count(self, obj):
        return obj.orders.count()


class AdminSerializer(serializers.ModelSerializer):
    """Серіалізатор для адміністратора"""

    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Admin
        fields = [
            'id', 'user', 'user_name', 'role',
            'can_manage_catalog', 'can_view_reports', 'can_manage_orders'
        ]