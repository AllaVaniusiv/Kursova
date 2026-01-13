from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Order, ShoppingCart, OrderBuilder
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    ShoppingCartSerializer,
    CartItemAddSerializer,
    CheckoutSerializer
)
from medications.models import Medication
from pharmacies.models import Pharmacy


class OrderViewSet(viewsets.ModelViewSet):
    """
    API для замовлень
    Використовує Factory Method і Builder patterns
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'order_type', 'is_paid']

    def get_queryset(self):
        """Користувач бачить тільки свої замовлення"""
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        """
        Створення замовлення через Builder Pattern
        """
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user = request.user

        try:
            # Використовуємо Builder pattern для створення замовлення
            builder = OrderBuilder(user)
            builder.set_order_type(data['order_type'])

            # Аптека
            if data.get('pharmacy_id'):
                pharmacy = Pharmacy.objects.get(id=data['pharmacy_id'])
                builder.set_pharmacy(pharmacy)

            # Додаємо товари
            for item in data['items']:
                medication = Medication.objects.get(id=item['medication_id'])
                builder.add_medication(medication, item['quantity'])

            # Додаткові параметри
            if data.get('delivery_address'):
                builder.set_delivery_address(data['delivery_address'])

            if data.get('payment_method'):
                builder.set_payment_method(data['payment_method'])

            if data.get('comment'):
                builder.set_comment(data['comment'])

            # Створюємо замовлення (сигнал автоматично надішле сповіщення)
            order = builder.build()

            # ❌ ВИДАЛЕНО: notify_order_created(order) - бо вже викликається в сигналі!

            # Повертаємо результат
            response_serializer = OrderSerializer(order)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        except Medication.DoesNotExist:
            return Response(
                {'error': 'Один або кілька медикаментів не знайдено'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Pharmacy.DoesNotExist:
            return Response(
                {'error': 'Аптека не знайдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Скасування замовлення
        """
        order = self.get_object()

        if order.status in ['completed', 'cancelled']:
            return Response(
                {'error': 'Неможливо скасувати це замовлення'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'cancelled'
        order.save()

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Зміна статусу замовлення (тільки для адмінів)
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Немає прав доступу'},
                status=status.HTTP_403_FORBIDDEN
            )

        order = self.get_object()
        new_status = request.data.get('status')

        if not new_status:
            return Response(
                {'error': 'Вкажіть новий статус'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def repeat_order(self, request, pk=None):
        """Повторити замовлення"""
        original_order = self.get_object()

        # Перевіряємо наявність
        unavailable_items = []
        for item in original_order.items.all():
            if not item.medication.is_available or not item.medication.is_in_stock():
                unavailable_items.append(item.medication.name)

        if unavailable_items:
            return Response({
                'success': False,
                'message': f'Деякі товари недоступні: {", ".join(unavailable_items)}',
                'unavailable_items': unavailable_items
            }, status=status.HTTP_400_BAD_REQUEST)

        # Додаємо в кошик
        cart, created = ShoppingCart.objects.get_or_create(user=request.user)

        for item in original_order.items.all():
            cart.add_item(item.medication, item.quantity)

        return Response({
            'success': True,
            'message': f'Товари з замовлення #{original_order.id} додано в кошик',
            'cart_items_count': cart.get_items_count()
        })

    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """Мої замовлення"""
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)


class ShoppingCartViewSet(viewsets.ViewSet):
    """API для кошика покупок"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Отримати кошик"""
        cart, created = ShoppingCart.objects.get_or_create(user=request.user)
        serializer = ShoppingCartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Додати товар в кошик"""
        serializer = CartItemAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            medication = Medication.objects.get(id=data['medication_id'])
            cart, created = ShoppingCart.objects.get_or_create(user=request.user)

            cart.add_item(medication, data['quantity'])

            response_serializer = ShoppingCartSerializer(cart)
            return Response(response_serializer.data)

        except Medication.DoesNotExist:
            return Response(
                {'error': 'Медикамент не знайдено'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Видалити товар з кошика"""
        medication_id = request.data.get('medication_id')

        if not medication_id:
            return Response(
                {'error': 'Вкажіть medication_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            medication = Medication.objects.get(id=medication_id)
            cart = ShoppingCart.objects.get(user=request.user)
            cart.remove_item(medication)

            serializer = ShoppingCartSerializer(cart)
            return Response(serializer.data)

        except Medication.DoesNotExist:
            return Response(
                {'error': 'Медикамент не знайдено'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ShoppingCart.DoesNotExist:
            return Response(
                {'error': 'Кошик порожній'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Очистити кошик"""
        try:
            cart = ShoppingCart.objects.get(user=request.user)
            cart.clear()

            serializer = ShoppingCartSerializer(cart)
            return Response(serializer.data)

        except ShoppingCart.DoesNotExist:
            return Response(
                {'error': 'Кошик порожній'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """Оформлення замовлення з кошика"""
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            cart = ShoppingCart.objects.get(user=request.user)

            pharmacy = None
            if data.get('pharmacy_id'):
                pharmacy = Pharmacy.objects.get(id=data['pharmacy_id'])

            # Оформлення через метод checkout (використовує Builder)
            order = cart.checkout(
                order_type=data['order_type'],
                pharmacy=pharmacy,
                delivery_address=data.get('delivery_address'),
                payment_method=data.get('payment_method')
            )

            order_serializer = OrderSerializer(order)
            return Response(order_serializer.data, status=status.HTTP_201_CREATED)

        except ShoppingCart.DoesNotExist:
            return Response(
                {'error': 'Кошик порожній'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Pharmacy.DoesNotExist:
            return Response(
                {'error': 'Аптека не знайдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )