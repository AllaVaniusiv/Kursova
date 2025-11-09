from rest_framework import serializers
from .models import Pharmacy, PharmacyStock


class PharmacySerializer(serializers.ModelSerializer):
    """Серіалізатор для аптек"""

    class Meta:
        model = Pharmacy
        fields = [
            'id', 'name', 'address', 'city', 'phone',
            'email', 'working_hours', 'is_active',
            'latitude', 'longitude', 'created_at'
        ]
        read_only_fields = ['created_at']


class PharmacyStockSerializer(serializers.ModelSerializer):
    """Серіалізатор для залишків в аптеках"""

    pharmacy_name = serializers.CharField(source='pharmacy.name', read_only=True)
    medication_name = serializers.CharField(source='medication.name', read_only=True)
    medication_price = serializers.DecimalField(
        source='medication.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = PharmacyStock
        fields = [
            'id', 'pharmacy', 'pharmacy_name', 'medication',
            'medication_name', 'medication_price', 'quantity',
            'last_updated'
        ]
        read_only_fields = ['last_updated']


class MedicationAvailabilitySerializer(serializers.Serializer):
    """Серіалізатор для перевірки наявності препарату"""

    medication_id = serializers.IntegerField()
    medication_name = serializers.CharField()
    available_pharmacies = serializers.ListField(
        child=serializers.DictField()
    )
    total_quantity = serializers.IntegerField()