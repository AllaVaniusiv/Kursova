from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import User
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """
    API для користувачів
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """Реєстрація доступна всім, інше тільки для авторизованих"""
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Різні serializers для різних дій"""
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action in ['me', 'update_profile']:
            return UserProfileSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        """
        Реєстрація нового користувача
        POST /api/users/
        {
            "username": "new_user",
            "email": "user@example.com",
            "password": "password123",
            "password_confirm": "password123",
            "first_name": "Іван",
            "last_name": "Петров",
            "phone": "+380671234567"
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                'message': 'Користувача успішно зареєстровано',
                'user': UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Отримати профіль поточного користувача
        GET /api/users/me/
        """
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """
        Оновити профіль поточного користувача
        PUT/PATCH /api/users/update_profile/
        {
            "first_name": "Іван",
            "last_name": "Петров",
            "phone": "+380671234567",
            "email_notifications": true
        }
        """
        partial = request.method == 'PATCH'
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """
        Замовлення поточного користувача
        GET /api/users/my_orders/
        """
        from orders.models import Order
        from orders.serializers import OrderSerializer

        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)

        return Response({
            'count': orders.count(),
            'orders': serializer.data
        })

    @action(detail=False, methods=['get'])
    def my_notifications(self, request):
        """
        Сповіщення поточного користувача
        GET /api/users/my_notifications/
        """
        from notifications.models import Notification

        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:20]

        unread_count = notifications.filter(is_read=False).count()

        notifications_data = []
        for notif in notifications:
            notifications_data.append({
                'id': notif.id,
                'type': notif.get_notification_type_display(),
                'message': notif.message,
                'is_read': notif.is_read,
                'created_at': notif.created_at
            })

        return Response({
            'unread_count': unread_count,
            'notifications': notifications_data
        })

    @action(detail=False, methods=['post'])
    def mark_notifications_read(self, request):
        """
        Позначити сповіщення як прочитані
        POST /api/users/mark_notifications_read/
        {"notification_ids": [1, 2, 3]}
        """
        from notifications.models import Notification

        notification_ids = request.data.get('notification_ids', [])

        if notification_ids:
            Notification.objects.filter(
                id__in=notification_ids,
                user=request.user
            ).update(is_read=True)
        else:
            # Позначити всі як прочитані
            Notification.objects.filter(
                user=request.user,
                is_read=False
            ).update(is_read=True)

        return Response({'message': 'Сповіщення позначені як прочитані'})

    @action(detail=False, methods=['get'])
    def bonus_info(self, request):
        """
        Інформація про бонуси
        GET /api/users/bonus_info/
        """
        user = request.user

        return Response({
            'bonus_points': user.bonus_points,
            'card_type': user.get_card_type_display(),
            'discount': user.get_discount(),
            'orders_count': user.orders.count(),
            'total_spent': sum(
                order.total_price
                for order in user.orders.filter(status='completed')
            )
        })