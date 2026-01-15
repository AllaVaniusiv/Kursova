from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import Medication, MedicationReview, medication_catalog
from .serializers import (
    MedicationSerializer,
    MedicationListSerializer,
    MedicationReviewSerializer
)


class MedicationViewSet(viewsets.ModelViewSet):
    """
    API для медикаментів
    Використовує Singleton pattern (medication_catalog)
    """
    queryset = Medication.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_prescription', 'is_available']
    search_fields = ['name', 'manufacturer', 'active_ingredient']
    ordering_fields = ['price', 'name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        """Повертає різні serializers для списку і деталей"""
        if self.action == 'list':
            return MedicationListSerializer
        return MedicationSerializer

    def get_permissions(self):
        """Права доступу"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Тільки адміни можуть змінювати
            permission_classes = [IsAuthenticated]
        else:
            # Всі можуть читати
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def search_catalog(self, request):
        """
        Пошук через Singleton catalog
        GET /api/medications/search_catalog/?query=аспірин&category=analgesic
        """
        query = request.query_params.get('query', None)
        category = request.query_params.get('category', None)
        is_prescription = request.query_params.get('is_prescription', None)

        # Конвертуємо is_prescription в boolean
        if is_prescription is not None:
            is_prescription = is_prescription.lower() == 'true'

        # Використовуємо Singleton pattern
        medications = medication_catalog.search_medications(
            query=query,
            category=category,
            is_prescription=is_prescription
        )

        serializer = MedicationListSerializer(medications, many=True)
        return Response({
            'count': len(medications),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def by_price_range(self, request):
        """
        Фільтр за ціною через Singleton
        GET /api/medications/by_price_range/?min_price=50&max_price=200
        """
        try:
            min_price = request.query_params.get('min_price', None)
            max_price = request.query_params.get('max_price', None)

            if min_price:
                min_price = float(min_price)
            if max_price:
                max_price = float(max_price)

            # Використовуємо Singleton pattern
            medications = medication_catalog.filter_by_price_range(
                min_price=min_price,
                max_price=max_price
            )

            serializer = MedicationListSerializer(medications, many=True)
            return Response({
                'count': len(medications),
                'results': serializer.data
            })
        except ValueError:
            return Response(
                {'error': 'Невірний формат ціни'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Тільки доступні медикаменти через Singleton
        GET /api/medications/available/
        """
        medications = medication_catalog.get_available_medications()
        serializer = MedicationListSerializer(medications, many=True)
        return Response({
            'count': len(medications),
            'results': serializer.data
        })

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """
        Перевірка наявності в аптеках
        GET /api/medications/{id}/availability/
        """
        medication = self.get_object()

        from pharmacies.models import PharmacyStock
        stocks = PharmacyStock.objects.filter(
            medication=medication,
            quantity__gt=0
        ).select_related('pharmacy')

        pharmacies_data = []
        for stock in stocks:
            pharmacies_data.append({
                'pharmacy_id': stock.pharmacy.id,
                'pharmacy_name': stock.pharmacy.name,
                'address': stock.pharmacy.address,
                'quantity': stock.quantity,
                'phone': stock.pharmacy.phone
            })

        return Response({
            'medication_id': medication.id,
            'medication_name': medication.name,
            'total_quantity': medication.get_total_stock(),
            'available_pharmacies': pharmacies_data
        })

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """
        Відгуки про медикамент
        GET /api/medications/{id}/reviews/
        """
        medication = self.get_object()
        reviews = medication.reviews.all()
        serializer = MedicationReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class MedicationReviewViewSet(viewsets.ModelViewSet):
    """
    API для відгуків про медикаменти
    """
    queryset = MedicationReview.objects.all()
    serializer_class = MedicationReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Автоматично встановлює поточного користувача"""
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Фільтр за медикаментом"""
        queryset = MedicationReview.objects.all()
        medication_id = self.request.query_params.get('medication', None)

        if medication_id is not None:
            queryset = queryset.filter(medication_id=medication_id)

        return queryset