from django.db import models
from django.core.validators import MinValueValidator


class Medication(models.Model):

    CATEGORY_CHOICES = [
        ('analgesic', 'Знеболююче'),
        ('antibiotic', 'Антибіотик'),
        ('vitamin', 'Вітаміни'),
        ('antiseptic', 'Антисептик'),
        ('cardiovascular', 'Серцево-судинні'),
        ('gastrointestinal', 'Шлунково-кишкові'),
        ('dermatological', 'Дерматологічні'),
        ('other', 'Інше'),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name="Назва"
    )

    description = models.TextField(
        verbose_name="Опис",
        blank=True
    )

    manufacturer = models.CharField(
        max_length=200,
        verbose_name="Виробник"
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name="Категорія"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Ціна"
    )

    is_prescription = models.BooleanField(
        default=False,
        verbose_name="Рецептурний"
    )

    active_ingredient = models.CharField(
        max_length=200,
        verbose_name="Діюча речовина",
        blank=True
    )

    dosage = models.CharField(
        max_length=100,
        verbose_name="Дозування",
        blank=True
    )

    image = models.ImageField(
        upload_to='medications/',
        verbose_name="Зображення",
        blank=True,
        null=True
    )

    is_available = models.BooleanField(
        default=True,
        verbose_name="Доступний"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата додавання"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата оновлення"
    )

    class Meta:
        verbose_name = "Медикамент"
        verbose_name_plural = "Медикаменти"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['is_prescription']),
        ]

    def __str__(self):
        return f"{self.name} ({self.manufacturer})"

    def get_total_stock(self):
        """Повертає загальну кількість в усіх аптеках"""
        from pharmacies.models import PharmacyStock
        total = PharmacyStock.objects.filter(
            medication=self
        ).aggregate(models.Sum('quantity'))['quantity__sum']
        return total or 0

    def is_in_stock(self):
        """Перевіряє чи є препарат в наявності"""
        return self.get_total_stock() > 0


class MedicationCatalogManager:
    _instance = None
    _medications = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MedicationCatalogManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

    def _load_medications(self):
        """Завантажує всі медикаменти з БД"""
        self._medications = list(Medication.objects.all())

    def get_all_medications(self):
        """Повертає всі медикаменти"""
        if self._medications is None:
            self._load_medications()
        return self._medications

    def search_medications(self, query=None, category=None, is_prescription=None):
        medications = Medication.objects.all()

        if query:
            medications = medications.filter(
                models.Q(name__icontains=query) |
                models.Q(manufacturer__icontains=query) |
                models.Q(active_ingredient__icontains=query)
            )

        if category:
            medications = medications.filter(category=category)

        if is_prescription is not None:
            medications = medications.filter(is_prescription=is_prescription)

        return list(medications)

    def get_medication_by_id(self, medication_id):
        """Отримує медикамент за ID"""
        try:
            return Medication.objects.get(id=medication_id)
        except Medication.DoesNotExist:
            return None

    def filter_by_price_range(self, min_price=None, max_price=None):
        """Фільтрує медикаменти за ціною"""
        medications = Medication.objects.all()

        if min_price is not None:
            medications = medications.filter(price__gte=min_price)

        if max_price is not None:
            medications = medications.filter(price__lte=max_price)

        return list(medications)

    def get_available_medications(self):
        """Повертає тільки доступні медикаменти"""
        return list(Medication.objects.filter(is_available=True))

    def reload_catalog(self):
        """Перезавантажує каталог з БД"""
        self._load_medications()

    @classmethod
    def get_instance(cls):
        """Статичний метод для отримання єдиного екземпляру"""
        return cls()


# Глобальний екземпляр каталогу (Singleton)
medication_catalog = MedicationCatalogManager.get_instance()


class MedicationReview(models.Model):
    """
    Відгуки про медикаменти
    """
    medication = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Медикамент"
    )

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='medication_reviews',
        verbose_name="Користувач"
    )

    rating = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Оцінка (1-5)"
    )

    comment = models.TextField(
        verbose_name="Коментар",
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата відгуку"
    )

    class Meta:
        verbose_name = "Відгук про медикамент"
        verbose_name_plural = "Відгуки про медикаменти"
        unique_together = ['medication', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.medication.name}: {self.rating}/5"