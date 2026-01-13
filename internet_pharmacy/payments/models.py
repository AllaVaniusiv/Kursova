from django.db import models
from abc import ABC, abstractmethod
from decimal import Decimal
import random
import string


class PaymentStrategy(ABC):

    @abstractmethod
    def pay(self, amount):
        """Виконує оплату"""
        pass

    @abstractmethod
    def validate(self):
        """Валідує можливість оплати"""
        pass

    @abstractmethod
    def get_payment_info(self):
        """Повертає інформацію про спосіб оплати"""
        pass


class CardPaymentStrategy(PaymentStrategy):

    def __init__(self, card_number, card_holder, cvv, expiry_date):
        self.card_number = card_number
        self.card_holder = card_holder
        self.cvv = cvv
        self.expiry_date = expiry_date

    def validate(self):
        """Валідує дані картки"""
        # Перевірка довжини номера картки
        if len(self.card_number.replace(' ', '')) != 16:
            return False, "Невірний номер картки"

        # Перевірка CVV
        if len(str(self.cvv)) != 3:
            return False, "Невірний CVV код"

        # Перевірка власника
        if not self.card_holder or len(self.card_holder) < 3:
            return False, "Невірне ім'я власника картки"

        return True, "Валідація пройшла успішно"

    def pay(self, amount):
        """Виконує оплату карткою"""
        is_valid, message = self.validate()

        if not is_valid:
            return {
                'success': False,
                'message': message,
                'transaction_id': None
            }

        # Імітація обробки платежу
        transaction_id = self._generate_transaction_id()

        return {
            'success': True,
            'message': f'Оплата {amount} грн картою успішна',
            'transaction_id': transaction_id,
            'payment_method': 'card',
            'last_digits': self.card_number[-4:]
        }

    def get_payment_info(self):
        """Інформація про оплату"""
        return {
            'method': 'Банківська картка',
            'details': f'**** **** **** {self.card_number[-4:]}'
        }

    def _generate_transaction_id(self):
        """Генерує ID транзакції"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class CashPaymentStrategy(PaymentStrategy):
    """
    Стратегія оплати готівкою
    """

    def __init__(self, payment_location=None):
        self.payment_location = payment_location

    def validate(self):
        """Валідація готівкової оплати"""
        return True, "Оплата готівкою доступна"

    def pay(self, amount):
        """Виконує оплату готівкою"""
        return {
            'success': True,
            'message': f'Оплата {amount} грн готівкою при отриманні',
            'transaction_id': None,
            'payment_method': 'cash',
            'location': self.payment_location or 'При отриманні'
        }

    def get_payment_info(self):
        """Інформація про оплату"""
        return {
            'method': 'Готівка',
            'details': self.payment_location or 'При отриманні'
        }


class OnlinePaymentStrategy(PaymentStrategy):
    """
    Стратегія онлайн оплати (через платіжні системи)
    """

    def __init__(self, payment_system='privat24'):
        self.payment_system = payment_system
        self.session_id = None

    def validate(self):
        """Валідація онлайн оплати"""
        if self.payment_system not in ['privat24', 'liqpay', 'wayforpay']:
            return False, "Невідома платіжна система"
        return True, "Платіжна система доступна"

    def pay(self, amount):
        """Виконує онлайн оплату"""
        is_valid, message = self.validate()

        if not is_valid:
            return {
                'success': False,
                'message': message,
                'transaction_id': None
            }

        # Генеруємо сесію для оплати
        self.session_id = self._generate_session_id()

        return {
            'success': True,
            'message': f'Перенаправлення на {self.payment_system}',
            'transaction_id': self.session_id,
            'payment_method': 'online',
            'payment_url': f'https://{self.payment_system}.com/pay/{self.session_id}'
        }

    def get_payment_info(self):
        """Інформація про оплату"""
        return {
            'method': f'Онлайн оплата ({self.payment_system})',
            'details': f'Сесія: {self.session_id}'
        }

    def _generate_session_id(self):
        """Генерує ID сесії"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))


class DeliveryStrategy(ABC):
    """
    Абстрактна стратегія доставки
    """

    @abstractmethod
    def deliver(self, order):
        """Організовує доставку"""
        pass

    @abstractmethod
    def calculate_cost(self, order):
        """Розраховує вартість доставки"""
        pass

    @abstractmethod
    def get_delivery_time(self):
        """Повертає час доставки"""
        pass


class CourierDeliveryStrategy(DeliveryStrategy):

    def __init__(self, address, delivery_time=None):
        self.address = address
        self.delivery_time = delivery_time
        self.base_cost = Decimal('50.00')

    def deliver(self, order):
        """Організовує доставку кур'єром"""
        return {
            'method': 'courier',
            'address': self.address,
            'estimated_time': self.delivery_time or '2-3 години',
            'cost': self.calculate_cost(order),
            'courier_assigned': True
        }

    def calculate_cost(self, order):
        """Розраховує вартість доставки"""
        cost = self.base_cost

        # Безкоштовна доставка для преміум
        if order.user.card_type == 'premium':
            cost = Decimal('0.00')

        # Знижка для великих замовлень
        elif order.subtotal > 500:
            cost = cost * Decimal('0.5')  # 50% знижка

        return cost

    def get_delivery_time(self):
        """Час доставки"""
        return self.delivery_time or '2-3 години'


class ExpressDeliveryStrategy(DeliveryStrategy):


    def __init__(self, address):
        self.address = address
        self.base_cost = Decimal('100.00')

    def deliver(self, order):
        """Організовує експрес-доставку"""
        return {
            'method': 'express',
            'address': self.address,
            'estimated_time': '60 хвилин',
            'cost': self.calculate_cost(order),
            'priority': 'high'
        }

    def calculate_cost(self, order):
        """Розраховує вартість експрес-доставки"""
        cost = self.base_cost

        # Невелика знижка для преміум
        if order.user.card_type == 'premium':
            cost = cost * Decimal('0.8')  # 20% знижка

        return cost

    def get_delivery_time(self):
        """Час доставки"""
        return '60 хвилин'


class SelfPickupStrategy(DeliveryStrategy):
    """
    Стратегія самовивозу
    """

    def __init__(self, pharmacy):
        self.pharmacy = pharmacy

    def deliver(self, order):
        """Організовує самовивіз"""
        return {
            'method': 'pickup',
            'pharmacy': self.pharmacy.name,
            'address': self.pharmacy.address,
            'estimated_time': '30 хвилин',
            'cost': Decimal('0.00'),
            'ready_for_pickup': False
        }

    def calculate_cost(self, order):
        """Самовивіз безкоштовний"""
        return Decimal('0.00')

    def get_delivery_time(self):
        """Час приготування"""
        return '30 хвилин'


class Payment(models.Model):

    PAYMENT_METHODS = [
        ('card', 'Банківська картка'),
        ('cash', 'Готівка'),
        ('online', 'Онлайн оплата'),
    ]

    PAYMENT_STATUS = [
        ('pending', 'Очікує оплати'),
        ('processing', 'Обробляється'),
        ('completed', 'Завершено'),
        ('failed', 'Помилка'),
        ('refunded', 'Повернено'),
    ]

    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name="Замовлення"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сума"
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        verbose_name="Спосіб оплати"
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending',
        verbose_name="Статус"
    )

    transaction_id = models.CharField(
        max_length=100,
        verbose_name="ID транзакції",
        blank=True,
        null=True
    )

    payment_details = models.JSONField(
        verbose_name="Деталі платежу",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата створення"
    )

    paid_at = models.DateTimeField(
        verbose_name="Дата оплати",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Платіж"
        verbose_name_plural = "Платежі"
        ordering = ['-created_at']

    def __str__(self):
        return f"Платіж #{self.id} - {self.amount} грн"

    def process_payment(self, strategy: PaymentStrategy):
        """
        Обробляє платіж використовуючи Strategy pattern
        """
        self.status = 'processing'
        self.save()

        # Виконуємо оплату через стратегію
        result = strategy.pay(self.amount)

        if result['success']:
            self.status = 'completed'
            self.transaction_id = result.get('transaction_id')
            self.payment_details = result

            from django.utils import timezone
            self.paid_at = timezone.now()

            # Оновлюємо статус замовлення
            self.order.is_paid = True
            self.order.save()
        else:
            self.status = 'failed'
            self.payment_details = result

        self.save()
        return result


class Delivery(models.Model):
    """
    Модель доставки
    """
    DELIVERY_METHODS = [
        ('courier', 'Кур\'єр'),
        ('express', 'Експрес'),
        ('pickup', 'Самовивіз'),
    ]

    DELIVERY_STATUS = [
        ('pending', 'Очікує'),
        ('preparing', 'Готується'),
        ('on_way', 'В дорозі'),
        ('delivered', 'Доставлено'),
        ('cancelled', 'Скасовано'),
    ]

    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='delivery',
        verbose_name="Замовлення"
    )

    delivery_method = models.CharField(
        max_length=20,
        choices=DELIVERY_METHODS,
        verbose_name="Спосіб доставки"
    )

    status = models.CharField(
        max_length=20,
        choices=DELIVERY_STATUS,
        default='pending',
        verbose_name="Статус"
    )

    delivery_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Вартість доставки"
    )

    estimated_time = models.CharField(
        max_length=100,
        verbose_name="Орієнтовний час",
        blank=True
    )

    delivery_details = models.JSONField(
        verbose_name="Деталі доставки",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата створення"
    )

    delivered_at = models.DateTimeField(
        verbose_name="Дата доставки",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Доставка"
        verbose_name_plural = "Доставки"
        ordering = ['-created_at']

    def __str__(self):
        return f"Доставка #{self.id} - {self.get_delivery_method_display()}"

    def organize_delivery(self, strategy: DeliveryStrategy):
        """
        Організовує доставку використовуючи Strategy pattern
        """
        # Отримуємо деталі доставки
        result = strategy.deliver(self.order)

        # Розраховуємо вартість
        self.delivery_cost = strategy.calculate_cost(self.order)
        self.estimated_time = strategy.get_delivery_time()
        self.delivery_details = result

        # Оновлюємо вартість доставки в замовленні
        self.order.delivery_cost = self.delivery_cost
        self.order.save()
        self.order.calculate_total()

        self.save()
        return result