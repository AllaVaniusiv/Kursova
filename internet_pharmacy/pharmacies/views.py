from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import Pharmacy, PharmacyStock
from .serializers import PharmacySerializer, PharmacyStockSerializer


class PharmacyViewSet(viewsets.ModelViewSet):
    """
    API для аптек
    """
    queryset = Pharmacy.objects.filter(is_active=True)
    serializer_class = PharmacySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['city', 'is_active']

    def get_permissions(self):
        """Читання для всіх, зміни тільки для адмінів"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get'])
    def stock(self, request, pk=None):
        """
        Залишки в конкретній аптеці
        GET /api/pharmacies/{id}/stock/
        """
        pharmacy = self.get_object()
        stocks = PharmacyStock.objects.filter(
            pharmacy=pharmacy,
            quantity__gt=0
        ).select_related('medication')

        serializer = PharmacyStockSerializer(stocks, many=True)
        return Response({
            'pharmacy': PharmacySerializer(pharmacy).data,
            'stock': serializer.data
        })

    @action(detail=True, methods=['get'])
    def check_medication(self, request, pk=None):
        """
        Перевірка наявності конкретного препарату в аптеці
        GET /api/pharmacies/{id}/check_medication/?medication_id=1
        """
        pharmacy = self.get_object()
        medication_id = request.query_params.get('medication_id', None)

        if not medication_id:
            return Response(
                {'error': 'Вкажіть medication_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from medications.models import Medication
            medication = Medication.objects.get(id=medication_id)

            is_available = pharmacy.check_availability(medication)
            quantity = pharmacy.get_medication_quantity(medication)

            return Response({
                'pharmacy': pharmacy.name,
                'medication': medication.name,
                'is_available': is_available,
                'quantity': quantity
            })
        except Medication.DoesNotExist:
            return Response(
                {'error': 'Медикамент не знайдено'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def by_city(self, request):
        """
        Аптеки по містах
        GET /api/pharmacies/by_city/?city=Львів
        """
        city = request.query_params.get('city', None)

        if city:
            pharmacies = Pharmacy.objects.filter(city__icontains=city, is_active=True)
        else:
            pharmacies = Pharmacy.objects.filter(is_active=True)

        serializer = self.get_serializer(pharmacies, many=True)
        return Response({
            'city': city or 'Всі',
            'count': pharmacies.count(),
            'results': serializer.data
        })


class PharmacyStockViewSet(viewsets.ModelViewSet):
    """
    API для залишків в аптеках
    """
    queryset = PharmacyStock.objects.all()
    serializer_class = PharmacyStockSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['pharmacy', 'medication']

    def get_queryset(self):
        """Фільтр за аптекою або медикаментом"""
        queryset = PharmacyStock.objects.all()

        pharmacy_id = self.request.query_params.get('pharmacy', None)
        medication_id = self.request.query_params.get('medication', None)

        if pharmacy_id:
            queryset = queryset.filter(pharmacy_id=pharmacy_id)

        if medication_id:
            queryset = queryset.filter(medication_id=medication_id)

        return queryset.select_related('pharmacy', 'medication')