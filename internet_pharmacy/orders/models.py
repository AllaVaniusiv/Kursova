from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from abc import ABC, abstractmethod


class Order(models.Model):
    """
    Базова модель замовлення
    """
    ORDER_STATUS = [
        ('pending', 'Очікує обробки'),
        ('confirmed', 'Підтверджено'),
        ('preparing', 'Готується'),
        ('ready', 'Готове до видачі'),
        ('in_delivery', 'В доставці'),
        ('completed', 'Завершено'),
        ('cancelled', 'Скасовано'),
    ]

    ORDER_TYPES = [
        ('delivery', 'Доставка'),
        ('pickup', 'Самовивіз'),
    ]

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Користувач"
    )

    order_type = models.CharField(
        max_length=20,
        choices=ORDER_TYPES,
        verbose_name="Тип замовлення"
    )

    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS,
        default='pending',
        verbose_name="Статус"
    )

    pharmacy = models.ForeignKey(
        'pharmacies.Pharmacy',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name="Аптека"
    )

    # Ціни
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Сума без знижки"
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Сума знижки"
    )

    delivery_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Вартість доставки"
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Загальна сума"
    )

    # Інформація про доставку
    delivery_address = models.CharField(
        max_length=300,
        verbose_name="Адреса доставки",
        blank=True
    )

    delivery_time = models.DateTimeField(
        verbose_name="Час доставки",
        null=True,
        blank=True
    )

    # Інформація про оплату
    payment_method = models.CharField(
        max_length=50,
        verbose_name="Спосіб оплати",
        blank=True
    )

    is_paid = models.BooleanField(
        default=False,
        verbose_name="Оплачено"
    )

    # Коментар
    comment = models.TextField(
        verbose_name="Коментар",
        blank=True
    )

    # Дати
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата створення"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата оновлення"
    )

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ['-created_at']

    def __str__(self):
        return f"Замовлення #{self.id} - {self.user.username}"

    def calculate_total(self):
        """Розраховує загальну суму замовлення"""
        # Підсумок товарів
        self.subtotal = sum(
            item.get_total_price()
            for item in self.items.all()
        )

        # Знижка від картки користувача
        discount_percent = self.user.get_discount()
        self.discount_amount = self.subtotal * Decimal(discount_percent / 100)

        # Загальна сума
        self.total_price = self.subtotal - self.discount_amount + self.delivery_cost
        self.save()

    def add_bonus_points(self):
        """Нараховує бонусні бали користувачу"""
        # 1% від суми замовлення
        points = int(self.total_price)
        self.user.add_bonus_points(points)


class OrderItem(models.Model):
    """
    Товар в замовленні
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Замовлення"
    )

    medication = models.ForeignKey(
        'medications.Medication',
        on_delete=models.CASCADE,
        verbose_name="Медикамент"
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Кількість"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Ціна за одиницю"
    )

    class Meta:
        verbose_name = "Товар в замовленні"
        verbose_name_plural = "Товари в замовленні"

    def __str__(self):
        return f"{self.medication.name} x {self.quantity}"

    # def get_total_price(self):
    #     """Повертає загальну ціну за товар"""
    #     return self.price * self.quantity

    def get_total_price(self):
        """Повертає загальну ціну за товар"""
        if self.price is None:
            return 0
        return self.price * self.quantity

    # def save(self, *args, **kwargs):
    #     # Зберігаємо ціну на момент замовлення
    #     if not self.price:
    #         self.price = self.medication.price
    #     super().save(*args, **kwargs)
    def save(self, *args, **kwargs):
        # Зберігаємо ціну на момент замовлення
        if self.price is None and self.medication:
            self.price = self.medication.price
        super().save(*args, **kwargs)


# ============= FACTORY METHOD PATTERN =============

class OrderFactory(ABC):
    """
    Абстрактна фабрика для створення замовлень
    Factory Method Pattern
    """

    @abstractmethod
    def create_order(self, user, pharmacy=None):
        """Створює замовлення певного типу"""
        pass

    def _set_common_fields(self, order, user):
        """Встановлює спільні поля для всіх замовлень"""
        order.user = user
        order.save()
        return order


class DeliveryOrderFactory(OrderFactory):
    """
    Фабрика для створення замовлень з доставкою
    """

    def create_order(self, user, pharmacy=None):
        order = Order(
            order_type='delivery',
            user=user,
            pharmacy=pharmacy,
            delivery_cost=Decimal('50.00')  # Базова вартість доставки
        )
        order.save()
        return order


class PickupOrderFactory(OrderFactory):
    """
    Фабрика для створення замовлень з самовивозом
    """

    def create_order(self, user, pharmacy=None):
        if not pharmacy:
            raise ValueError("Для самовивозу потрібно вказати аптеку")

        order = Order(
            order_type='pickup',
            user=user,
            pharmacy=pharmacy,
            delivery_cost=Decimal('0.00')  # Без доставки
        )
        order.save()
        return order


def get_order_factory(order_type):
    """
    Повертає відповідну фабрику залежно від типу замовлення
    """
    factories = {
        'delivery': DeliveryOrderFactory(),
        'pickup': PickupOrderFactory(),
    }
    return factories.get(order_type)


# ============= BUILDER PATTERN =============

class OrderBuilder:
    """
    Будівельник для покрокового створення замовлення
    Builder Pattern
    """

    def __init__(self, user):
        self.user = user
        self.order = None
        self.order_type = None
        self.pharmacy = None
        self.items = []
        self.delivery_address = None
        self.payment_method = None
        self.comment = None

    def set_order_type(self, order_type):
        """Встановлює тип замовлення"""
        self.order_type = order_type
        return self

    def set_pharmacy(self, pharmacy):
        """Встановлює аптеку"""
        self.pharmacy = pharmacy
        return self

    def add_medication(self, medication, quantity=1):
        """Додає медикамент до замовлення"""
        self.items.append({
            'medication': medication,
            'quantity': quantity
        })
        return self

    def set_delivery_address(self, address):
        """Встановлює адресу доставки"""
        self.delivery_address = address
        return self

    def set_payment_method(self, method):
        """Встановлює спосіб оплати"""
        self.payment_method = method
        return self

    def set_comment(self, comment):
        """Додає коментар"""
        self.comment = comment
        return self

    def build(self):
        """
        Створює та повертає готове замовлення
        """
        if not self.order_type:
            raise ValueError("Тип замовлення не встановлено")

        if not self.items:
            raise ValueError("Замовлення порожнє")

        # Створюємо замовлення через фабрику
        factory = get_order_factory(self.order_type)
        self.order = factory.create_order(self.user, self.pharmacy)

        # Додаємо додаткові поля
        if self.delivery_address:
            self.order.delivery_address = self.delivery_address

        if self.payment_method:
            self.order.payment_method = self.payment_method

        if self.comment:
            self.order.comment = self.comment

        self.order.save()

        # Додаємо товари
        for item_data in self.items:
            OrderItem.objects.create(
                order=self.order,
                medication=item_data['medication'],
                quantity=item_data['quantity'],
                price=item_data['medication'].price
            )

        # Розраховуємо суму
        self.order.calculate_total()

        return self.order

    def reset(self):
        """Скидає будівельник для нового замовлення"""
        self.__init__(self.user)
        return self


class ShoppingCart(models.Model):
    """
    Кошик покупок
    """
    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name="Користувач"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата створення"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата оновлення"
    )

    class Meta:
        verbose_name = "Кошик"
        verbose_name_plural = "Кошики"

    def __str__(self):
        return f"Кошик {self.user.username}"

    def add_item(self, medication, quantity=1):
        """Додає товар в кошик"""
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            medication=medication,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item

    def remove_item(self, medication):
        """Видаляє товар з кошика"""
        CartItem.objects.filter(cart=self, medication=medication).delete()

    def clear(self):
        """Очищає кошик"""
        self.items.all().delete()

    def get_total_price(self):
        """Повертає загальну суму кошика"""
        return sum(item.get_total_price() for item in self.items.all())

    def get_items_count(self):
        """Повертає кількість товарів"""
        return sum(item.quantity for item in self.items.all())

    def checkout(self, order_type, pharmacy=None, delivery_address=None, payment_method=None):
        """
        Оформлення замовлення з кошика
        Використовує Builder pattern
        """
        if not self.items.exists():
            raise ValueError("Кошик порожній")

        # Створюємо замовлення через Builder
        builder = OrderBuilder(self.user)
        builder.set_order_type(order_type)

        if pharmacy:
            builder.set_pharmacy(pharmacy)

        if delivery_address:
            builder.set_delivery_address(delivery_address)

        if payment_method:
            builder.set_payment_method(payment_method)

        # Додаємо всі товари з кошика
        for item in self.items.all():
            builder.add_medication(item.medication, item.quantity)

        # Створюємо замовлення
        order = builder.build()

        # Очищаємо кошик
        self.clear()

        return order


class CartItem(models.Model):
    """
    Товар в кошику
    """
    cart = models.ForeignKey(
        ShoppingCart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Кошик"
    )

    medication = models.ForeignKey(
        'medications.Medication',
        on_delete=models.CASCADE,
        verbose_name="Медикамент"
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Кількість"
    )

    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата додавання"
    )

    class Meta:
        verbose_name = "Товар в кошику"
        verbose_name_plural = "Товари в кошику"
        unique_together = ['cart', 'medication']

    def __str__(self):
        return f"{self.medication.name} x {self.quantity}"

    def get_total_price(self):
        """Повертає загальну ціну за товар"""
        return self.medication.price * self.quantity