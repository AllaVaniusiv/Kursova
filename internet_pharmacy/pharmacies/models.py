from django.db import models


class Pharmacy(models.Model):
    """
    Модель аптеки в мережі
    """
    name = models.CharField(
        max_length=200,
        verbose_name="Назва"
    )

    address = models.CharField(
        max_length=300,
        verbose_name="Адреса"
    )

    city = models.CharField(
        max_length=100,
        verbose_name="Місто",
        default="Львів"
    )

    phone = models.CharField(
        max_length=15,
        verbose_name="Телефон"
    )

    email = models.EmailField(
        verbose_name="Email",
        blank=True
    )

    working_hours = models.CharField(
        max_length=100,
        verbose_name="Графік роботи",
        default="9:00-21:00"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна"
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Широта"
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Довгота"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата додавання"
    )

    class Meta:
        verbose_name = "Аптека"
        verbose_name_plural = "Аптеки"
        ordering = ['city', 'name']

    def __str__(self):
        return f"{self.name} - {self.address}"

    def check_availability(self, medication):
        """
        Перевіряє наявність препарату в аптеці
        """
        try:
            stock = PharmacyStock.objects.get(
                pharmacy=self,
                medication=medication
            )
            return stock.quantity > 0
        except PharmacyStock.DoesNotExist:
            return False

    def get_medication_quantity(self, medication):
        """
        Повертає кількість препарату в аптеці
        """
        try:
            stock = PharmacyStock.objects.get(
                pharmacy=self,
                medication=medication
            )
            return stock.quantity
        except PharmacyStock.DoesNotExist:
            return 0


class PharmacyStock(models.Model):
    """
    Залишки медикаментів в конкретній аптеці
    """
    pharmacy = models.ForeignKey(
        Pharmacy,
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name="Аптека"
    )

    medication = models.ForeignKey(
        'medications.Medication',
        on_delete=models.CASCADE,
        related_name='pharmacy_stocks',
        verbose_name="Медикамент"
    )

    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="Кількість"
    )

    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Останнє оновлення"
    )

    class Meta:
        verbose_name = "Залишок в аптеці"
        verbose_name_plural = "Залишки в аптеках"
        unique_together = ['pharmacy', 'medication']

    def __str__(self):
        return f"{self.medication.name} в {self.pharmacy.name}: {self.quantity} шт."