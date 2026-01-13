from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Order


# Зберігаємо старий статус перед збереженням
@receiver(pre_save, sender=Order)
def store_old_status(sender, instance, **kwargs):
    """Зберігає старий статус замовлення перед оновленням"""
    if instance.pk:  # Якщо це оновлення існуючого замовлення
        try:
            old_order = Order.objects.get(pk=instance.pk)
            instance._old_status = old_order.status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Order)
def send_status_notification(sender, instance, created, **kwargs):
    """Надсилає сповіщення при зміні статусу замовлення"""

    # Якщо це нове замовлення
    if created:
        from notifications.models import notify_order_created
        notify_order_created(instance)
        print(f"✉️ Відправлено сповіщення про створення замовлення #{instance.id}")
        return

    # Якщо статус змінився
    old_status = getattr(instance, '_old_status', None)

    if old_status and old_status != instance.status:
        from notifications.models import notify_order_status_changed
        notify_order_status_changed(instance, instance.status)
        print(
            f"✉️ Відправлено сповіщення про зміну статусу замовлення #{instance.id}: {old_status} → {instance.status}")



