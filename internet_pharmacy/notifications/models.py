from django.db import models
from abc import ABC, abstractmethod
from typing import List


class Observer(ABC):

    @abstractmethod
    def update(self, message, notification_type=None):
        """Отримує сповіщення"""
        pass

    @abstractmethod
    def get_contact_info(self):
        """Повертає контактну інформацію"""
        pass


class EmailObserver(Observer):

    def __init__(self, user):
        self.user = user

    def update(self, message, notification_type=None):
        """Надсилає email сповіщення"""
        if not self.user.email_notifications:
            return False

        subject = self._get_subject(notification_type)

        try:

            # Імітація надсилання
            print(f"📧 Email to {self.user.email}: {subject}")
            print(f"   {message}")

            # НЕ зберігаємо в БД окремо для email
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def get_contact_info(self):
        """Повертає email"""
        return self.user.email

    def _get_subject(self, notification_type):
        """Генерує тему листа"""
        subjects = {
            'order_created': '✅ Замовлення створено',
            'order_confirmed': '📦 Замовлення підтверджено',
            'order_ready': '✨ Замовлення готове',
            'order_delivered': '🎉 Замовлення доставлено',
            'promotion': '🎁 Спеціальна пропозиція',
            'bonus_added': '⭐ Нараховано бонуси',
            'medication_available': '💊 Препарат в наявності',
        }
        return subjects.get(notification_type, '📬 Повідомлення від Інтернет-аптеки')


class SMSObserver(Observer):
    """
    Спостерігач для SMS сповіщень
    """

    def __init__(self, user):
        self.user = user

    def update(self, message, notification_type=None):
        """Надсилає SMS сповіщення"""
        if not self.user.sms_notifications or not self.user.phone:
            return False

        try:
            # В реальному проекті тут буде інтеграція з SMS API
            # sms_service.send(self.user.phone, message)

            # Імітація надсилання
            print(f"📱 SMS to {self.user.phone}: {message[:50]}...")

            # НЕ зберігаємо в БД окремо для SMS
            return True
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False

    def get_contact_info(self):
        """Повертає телефон"""
        return self.user.phone


class PushObserver(Observer):
    """
    Спостерігач для push-сповіщень (в додатку)
    """

    def __init__(self, user):
        self.user = user

    def update(self, message, notification_type=None):
        """Надсилає push-сповіщення"""
        try:
            # В реальному проекті тут буде Firebase Cloud Messaging
            print(f"🔔 Push to {self.user.username}: {message}")

            # Зберігаємо в БД ТІЛЬКИ push (основне сповіщення для UI)
            Notification.objects.create(
                user=self.user,
                notification_type=notification_type or 'info',
                channel='push',
                message=message,
                is_sent=True
            )
            return True
        except Exception as e:
            print(f"Error sending push: {e}")
            return False

    def get_contact_info(self):
        """Повертає username"""
        return self.user.username


class NotificationService:

    def __init__(self):
        self._observers: List[Observer] = []

    def subscribe(self, observer: Observer):
        """Підписує спостерігача на сповіщення"""
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: Observer):
        """Відписує спостерігача"""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, message, notification_type=None):
        """
        Надсилає сповіщення всім підписаним спостерігачам
        """
        results = []
        for observer in self._observers:
            result = observer.update(message, notification_type)
            results.append(result)
        return results

    def notify_user(self, user, message, notification_type=None, channels=None):
        """
        Надсилає сповіщення конкретному користувачу через вибрані канали
        """
        if channels is None:
            channels = ['email', 'sms', 'push']

        observers = []

        if 'email' in channels and user.email_notifications:
            observers.append(EmailObserver(user))

        if 'sms' in channels and user.sms_notifications:
            observers.append(SMSObserver(user))

        if 'push' in channels:
            observers.append(PushObserver(user))

        # Підписуємо та надсилаємо
        for observer in observers:
            self.subscribe(observer)

        results = self.notify(message, notification_type)

        # Відписуємо після надсилання
        for observer in observers:
            self.unsubscribe(observer)

        return results


# Глобальний екземпляр сервісу сповіщень
notification_service = NotificationService()


# ============= Моделі для зберігання сповіщень =============

class Notification(models.Model):
    """
    Модель сповіщення (для історії)
    """
    NOTIFICATION_TYPES = [
        ('order_created', 'Замовлення створено'),
        ('order_confirmed', 'Замовлення підтверджено'),
        ('order_ready', 'Замовлення готове'),
        ('order_delivered', 'Замовлення доставлено'),
        ('order_cancelled', 'Замовлення скасовано'),
        ('promotion', 'Акція'),
        ('bonus_added', 'Нараховано бонуси'),
        ('medication_available', 'Препарат в наявності'),
        ('info', 'Інформація'),
    ]

    CHANNELS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push'),
    ]

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Користувач"
    )

    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
        verbose_name="Тип сповіщення"
    )

    channel = models.CharField(
        max_length=10,
        choices=CHANNELS,
        verbose_name="Канал"
    )

    message = models.TextField(
        verbose_name="Повідомлення"
    )

    is_sent = models.BooleanField(
        default=False,
        verbose_name="Надіслано"
    )

    is_read = models.BooleanField(
        default=False,
        verbose_name="Прочитано"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата створення"
    )

    sent_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата відправки"
    )

    class Meta:
        verbose_name = "Сповіщення"
        verbose_name_plural = "Сповіщення"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return f"{self.get_notification_type_display()} для {self.user.username}"

    def mark_as_read(self):
        """Позначає сповіщення як прочитане"""
        self.is_read = True
        self.save()


class NotificationTemplate(models.Model):
    """
    Шаблони сповіщень
    """
    NOTIFICATION_TYPES = Notification.NOTIFICATION_TYPES

    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
        unique=True,
        verbose_name="Тип сповіщення"
    )

    email_subject = models.CharField(
        max_length=200,
        verbose_name="Тема email",
        blank=True
    )

    email_template = models.TextField(
        verbose_name="Шаблон email",
        blank=True,
        help_text="Використовуйте {user_name}, {order_id}, {total_price} для підстановки"
    )

    sms_template = models.CharField(
        max_length=160,
        verbose_name="Шаблон SMS",
        blank=True,
        help_text="Максимум 160 символів"
    )

    push_template = models.CharField(
        max_length=200,
        verbose_name="Шаблон Push",
        blank=True
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активний"
    )

    class Meta:
        verbose_name = "Шаблон сповіщення"
        verbose_name_plural = "Шаблони сповіщень"

    def __str__(self):
        return self.get_notification_type_display()

    def render_message(self, channel, **context):
        """
        Рендерить повідомлення з підстановкою змінних
        """
        template_map = {
            'email': self.email_template,
            'sms': self.sms_template,
            'push': self.push_template,
        }

        template = template_map.get(channel, '')

        # Підстановка змінних
        try:
            message = template.format(**context)
        except KeyError:
            message = template

        return message


# ============= Допоміжні функції для Observer Pattern =============

def notify_order_created(order):
    """Сповіщення про створення замовлення"""
    message = f"Дякуємо за замовлення! Номер замовлення: #{order.id}. Ми повідомимо вас про зміну статусу замовлення."

    notification_service.notify_user(
        user=order.user,
        message=message,
        notification_type='order_created',
        channels=['push']  # Тільки push для UI
    )


def notify_order_status_changed(order, new_status):
    """Сповіщення про зміну статусу замовлення"""
    status_messages = {
        'confirmed': f'Ваше замовлення #{order.id} підтверджено і готується.',
        'ready': f'Ваше замовлення #{order.id} готове до видачі!',
        'in_delivery': f'Ваше замовлення #{order.id} передано кур\'єру.',
        'completed': f'Ваше замовлення #{order.id} успішно доставлено. Дякуємо!',
        'cancelled': f'Ваше замовлення #{order.id} скасовано.',
    }

    message = status_messages.get(new_status, f'Статус замовлення #{order.id} змінено.')

    # Визначаємо тип сповіщення залежно від статусу
    notification_type_map = {
        'confirmed': 'order_confirmed',
        'ready': 'order_ready',
        'in_delivery': 'order_ready',
        'completed': 'order_delivered',
        'cancelled': 'order_cancelled',
    }
    notification_type = notification_type_map.get(new_status, 'info')

    notification_service.notify_user(
        user=order.user,
        message=message,
        notification_type=notification_type,
        channels=['email', 'sms', 'push']
    )


def notify_bonus_added(user, points, reason):
    """Сповіщення про нарахування бонусів"""
    message = f"""
    Вітаємо! 🎉

    Вам нараховано {points} бонусних балів за {reason}.
    Всього бонусів: {user.bonus_points}

    Використовуйте бонуси при наступному замовленні!
    """

    notification_service.notify_user(
        user=user,
        message=message.strip(),
        notification_type='bonus_added',
        channels=['email', 'push']
    )


def notify_medication_available(user, medication):
    """Сповіщення про наявність препарату"""
    message = f"""
    Препарат в наявності! 💊

    {medication.name} ({medication.manufacturer})
    Ціна: {medication.price} грн

    Поспішайте оформити замовлення!
    """

    notification_service.notify_user(
        user=user,
        message=message.strip(),
        notification_type='medication_available',
        channels=['email', 'sms', 'push']
    )


def notify_promotion(users, promotion_text):
    """Розсилка акцій групі користувачів"""
    for user in users:
        notification_service.notify_user(
            user=user,
            message=promotion_text,
            notification_type='promotion',
            channels=['email', 'push']
        )