from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Серіалізатор для сповіщень"""

    type = serializers.CharField(source='get_notification_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'type',
            'notification_type',
            'channel',
            'message',
            'is_read',
            'is_sent',
            'created_at',
            'sent_at'
        ]
        read_only_fields = ['id', 'created_at', 'sent_at', 'is_sent']