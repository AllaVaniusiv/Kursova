from rest_framework import serializers
from .models import Medication, MedicationReview


class MedicationSerializer(serializers.ModelSerializer):
    """Серіалізатор для медикаментів"""

    total_stock = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Medication
        fields = [
            'id', 'name', 'description', 'manufacturer',
            'category', 'category_display', 'price',
            'is_prescription', 'active_ingredient', 'dosage',
            'image', 'is_available', 'total_stock', 'in_stock',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_total_stock(self, obj):
        """Загальна кількість в усіх аптеках"""
        return obj.get_total_stock()

    def get_in_stock(self, obj):
        """Чи є в наявності"""
        return obj.is_in_stock()


class MedicationListSerializer(serializers.ModelSerializer):
    """Скорочений серіалізатор для списку медикаментів"""

    category_display = serializers.CharField(source='get_category_display', read_only=True)
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Medication
        fields = [
            'id', 'name', 'manufacturer', 'category',
            'category_display', 'price', 'is_prescription',
            'image', 'in_stock'
        ]

    def get_in_stock(self, obj):
        return obj.is_in_stock()


class MedicationReviewSerializer(serializers.ModelSerializer):
    """Серіалізатор для відгуків"""

    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = MedicationReview
        fields = ['id', 'medication', 'user', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']

    def validate_rating(self, value):
        """Валідація рейтингу"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Рейтинг має бути від 1 до 5")
        return value