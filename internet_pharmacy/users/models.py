from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Розширена модель користувача
    Реалізує Observer патерн - може отримувати сповіщення
    """
    CARD_TYPES = [
        ('standard', 'Стандартна'),
        ('premium', 'Преміум'),
        ('social', 'Соціальна'),
    ]

    phone = models.CharField(
        max_length=15,
        verbose_name="Телефон",
        blank=True
    )

    date_of_birth = models.DateField(
        verbose_name="Дата народження",
        null=True,
        blank=True
    )

    card_type = models.CharField(
        max_length=20,
        choices=CARD_TYPES,
        default='standard',
        verbose_name="Тип картки"
    )

    bonus_points = models.IntegerField(
        default=0,
        verbose_name="Бонусні бали"
    )

    # Налаштування для сповіщень (Observer pattern)
    email_notifications = models.BooleanField(
        default=True,
        verbose_name="Email сповіщення"
    )

    sms_notifications = models.BooleanField(
        default=False,
        verbose_name="SMS сповіщення"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата реєстрації"
    )

    class Meta:
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"

    def __str__(self):
        return f"{self.username} ({self.get_card_type_display()})"

    def get_discount(self):
        """
        Повертає знижку залежно від типу картки
        Decorator pattern - різні рівні знижок
        """
        discounts = {
            'standard': 0,
            'premium': 10,
            'social': 5,
        }
        return discounts.get(self.card_type, 0)

    def add_bonus_points(self, points):
        """Додає бонусні бали"""
        self.bonus_points += points
        self.save()

    def update(self, message):
        """
        Метод для Observer патерну
        Викликається при надсиланні сповіщень
        """
        # Буде реалізовано в notifications app
        pass


class Admin(models.Model):
    """
    Адміністратор системи
    Розширює можливості звичайного користувача
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='admin_profile',
        verbose_name="Користувач"
    )

    role = models.CharField(
        max_length=50,
        default='administrator',
        verbose_name="Роль"
    )

    can_manage_catalog = models.BooleanField(
        default=True,
        verbose_name="Може керувати каталогом"
    )

    can_view_reports = models.BooleanField(
        default=True,
        verbose_name="Може переглядати звіти"
    )

    can_manage_orders = models.BooleanField(
        default=True,
        verbose_name="Може керувати замовленнями"
    )

    class Meta:
        verbose_name = "Адміністратор"
        verbose_name_plural = "Адміністратори"

    def __str__(self):
        return f"Admin: {self.user.username}"