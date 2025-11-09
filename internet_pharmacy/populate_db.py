"""
Скрипт для наповнення БД тестовими даними
Запуск: python manage.py shell < populate_db.py
АБО: python populate_db.py
"""

import os
import django
from decimal import Decimal

# Налаштування Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_core.settings')
django.setup()

from users.models import User, Admin
from medications.models import Medication, MedicationReview
from pharmacies.models import Pharmacy, PharmacyStock
from orders.models import Order, OrderItem, ShoppingCart
from payments.models import Payment, Delivery
from notifications.models import NotificationTemplate


def create_users():
    """Створює тестових користувачів"""
    print("📝 Створення користувачів...")

    # Звичайний користувач
    user1, created = User.objects.get_or_create(
        username='ivan_petrov',
        defaults={
            'email': 'ivan@example.com',
            'first_name': 'Іван',
            'last_name': 'Петров',
            'phone': '+380671234567',
            'card_type': 'standard',
            'bonus_points': 100,
            'email_notifications': True,
            'sms_notifications': True,
        }
    )
    if created:
        user1.set_password('password123')
        user1.save()
        print(f"  ✅ Створено: {user1.username} (standard)")

    # Преміум користувач
    user2, created = User.objects.get_or_create(
        username='maria_koval',
        defaults={
            'email': 'maria@example.com',
            'first_name': 'Марія',
            'last_name': 'Коваль',
            'phone': '+380672345678',
            'card_type': 'premium',
            'bonus_points': 500,
            'email_notifications': True,
            'sms_notifications': False,
        }
    )
    if created:
        user2.set_password('password123')
        user2.save()
        print(f"  ✅ Створено: {user2.username} (premium)")

    # Соціальна картка
    user3, created = User.objects.get_or_create(
        username='olga_shevchenko',
        defaults={
            'email': 'olga@example.com',
            'first_name': 'Ольга',
            'last_name': 'Шевченко',
            'phone': '+380673456789',
            'card_type': 'social',
            'bonus_points': 50,
            'email_notifications': True,
            'sms_notifications': True,
        }
    )
    if created:
        user3.set_password('password123')
        user3.save()
        print(f"  ✅ Створено: {user3.username} (social)")

    # Адміністратор
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@pharmacy.com',
            'first_name': 'Адмін',
            'last_name': 'Адміністратор',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()

        Admin.objects.create(
            user=admin_user,
            role='administrator',
            can_manage_catalog=True,
            can_view_reports=True,
            can_manage_orders=True
        )
        print(f"  ✅ Створено адміністратора: {admin_user.username}")

    return user1, user2, user3, admin_user


def create_pharmacies():
    """Створює аптеки"""
    print("\n🏥 Створення аптек...")

    pharmacies_data = [
        {
            'name': 'Аптека №1 (Центр)',
            'address': 'вул. Городоцька, 123',
            'city': 'Львів',
            'phone': '+380322123456',
            'working_hours': '8:00-22:00',
        },
        {
            'name': 'Аптека №2 (Сихів)',
            'address': 'вул. Наукова, 45',
            'city': 'Львів',
            'phone': '+380322234567',
            'working_hours': '9:00-21:00',
        },
        {
            'name': 'Аптека №3 (Франківський)',
            'address': 'вул. Під Дубом, 78',
            'city': 'Львів',
            'phone': '+380322345678',
            'working_hours': '24/7',
        },
    ]

    pharmacies = []
    for data in pharmacies_data:
        pharmacy, created = Pharmacy.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        pharmacies.append(pharmacy)
        if created:
            print(f"  ✅ Створено: {pharmacy.name}")

    return pharmacies


def create_medications():
    """Створює медикаменти"""
    print("\n💊 Створення медикаментів...")

    medications_data = [
        {
            'name': 'Аспірин',
            'manufacturer': 'Bayer',
            'category': 'analgesic',
            'price': Decimal('45.50'),
            'is_prescription': False,
            'active_ingredient': 'Ацетилсаліцилова кислота',
            'dosage': '500 мг',
            'description': 'Знеболююче та жарознижуюче засіб',
        },
        {
            'name': 'Парацетамол',
            'manufacturer': 'Дарниця',
            'category': 'analgesic',
            'price': Decimal('25.00'),
            'is_prescription': False,
            'active_ingredient': 'Парацетамол',
            'dosage': '500 мг',
            'description': 'Жарознижуючий та знеболюючий препарат',
        },
        {
            'name': 'Амоксицилін',
            'manufacturer': 'Sandoz',
            'category': 'antibiotic',
            'price': Decimal('120.00'),
            'is_prescription': True,
            'active_ingredient': 'Амоксицилін',
            'dosage': '500 мг',
            'description': 'Антибіотик широкого спектру дії',
        },
        {
            'name': 'Вітамін C',
            'manufacturer': 'Naturalis',
            'category': 'vitamin',
            'price': Decimal('85.00'),
            'is_prescription': False,
            'active_ingredient': 'Аскорбінова кислота',
            'dosage': '1000 мг',
            'description': 'Вітамін для зміцнення імунітету',
        },
        {
            'name': 'Вітамін D3',
            'manufacturer': 'Solgar',
            'category': 'vitamin',
            'price': Decimal('350.00'),
            'is_prescription': False,
            'active_ingredient': 'Холекальциферол',
            'dosage': '2000 МО',
            'description': 'Вітамін для кісток та імунітету',
        },
        {
            'name': 'Йод',
            'manufacturer': 'Фармак',
            'category': 'antiseptic',
            'price': Decimal('15.50'),
            'is_prescription': False,
            'active_ingredient': 'Розчин йоду',
            'dosage': '5%',
            'description': 'Антисептичний засіб',
        },
        {
            'name': 'Но-Шпа',
            'manufacturer': 'Chinoin',
            'category': 'gastrointestinal',
            'price': Decimal('95.00'),
            'is_prescription': False,
            'active_ingredient': 'Дротаверин',
            'dosage': '40 мг',
            'description': 'Спазмолітичний засіб',
        },
        {
            'name': 'Кардіомагніл',
            'manufacturer': 'Takeda',
            'category': 'cardiovascular',
            'price': Decimal('180.00'),
            'is_prescription': True,
            'active_ingredient': 'Ацетилсаліцилова кислота + Магній',
            'dosage': '75 мг',
            'description': 'Для профілактики серцево-судинних захворювань',
        },
    ]

    medications = []
    for data in medications_data:
        med, created = Medication.objects.get_or_create(
            name=data['name'],
            manufacturer=data['manufacturer'],
            defaults=data
        )
        medications.append(med)
        if created:
            print(f"  ✅ Створено: {med.name} - {med.price} грн")

    return medications


def create_pharmacy_stocks(pharmacies, medications):
    """Створює залишки в аптеках"""
    print("\n📦 Наповнення аптек товарами...")

    import random

    for pharmacy in pharmacies:
        for medication in medications:
            quantity = random.randint(5, 50)
            stock, created = PharmacyStock.objects.get_or_create(
                pharmacy=pharmacy,
                medication=medication,
                defaults={'quantity': quantity}
            )
            if created:
                print(f"  ✅ {pharmacy.name}: {medication.name} - {quantity} шт.")


def create_notification_templates():
    """Створює шаблони сповіщень"""
    print("\n📧 Створення шаблонів сповіщень...")

    templates_data = [
        {
            'notification_type': 'order_created',
            'email_subject': 'Замовлення #{order_id} створено',
            'email_template': 'Дякуємо за замовлення, {user_name}! Номер замовлення: #{order_id}. Сума: {total_price} грн.',
            'sms_template': 'Замовлення #{order_id} створено. Сума: {total_price} грн.',
            'push_template': 'Замовлення #{order_id} створено',
        },
        {
            'notification_type': 'order_confirmed',
            'email_subject': 'Замовлення #{order_id} підтверджено',
            'email_template': 'Ваше замовлення #{order_id} підтверджено і готується.',
            'sms_template': 'Замовлення #{order_id} підтверджено',
            'push_template': 'Замовлення підтверджено',
        },
        {
            'notification_type': 'bonus_added',
            'email_subject': 'Нараховано бонуси',
            'email_template': 'Вітаємо, {user_name}! Вам нараховано {points} бонусних балів.',
            'sms_template': 'Нараховано {points} бонусів',
            'push_template': '+{points} бонусів',
        },
    ]

    for data in templates_data:
        template, created = NotificationTemplate.objects.get_or_create(
            notification_type=data['notification_type'],
            defaults=data
        )
        if created:
            print(f"  ✅ Шаблон: {template.get_notification_type_display()}")


def create_sample_order(user, medications, pharmacy):
    """Створює тестове замовлення"""
    print("\n🛒 Створення тестового замовлення...")

    from orders.models import OrderBuilder

    # Використовуємо Builder pattern
    builder = OrderBuilder(user)
    order = builder \
        .set_order_type('delivery') \
        .set_pharmacy(pharmacy) \
        .add_medication(medications[0], quantity=2) \
        .add_medication(medications[3], quantity=1) \
        .set_delivery_address('вул. Шевченка, 10, кв. 5') \
        .set_payment_method('card') \
        .set_comment('Доставити до 18:00') \
        .build()

    print(f"  ✅ Створено замовлення #{order.id} на суму {order.total_price} грн")
    return order


def main():
    """Головна функція"""
    print("=" * 60)
    print("🚀 НАПОВНЕННЯ БАЗИ ДАНИХ ТЕСТОВИМИ ДАНИМИ")
    print("=" * 60)

    # Створюємо дані
    users = create_users()
    pharmacies = create_pharmacies()
    medications = create_medications()
    create_pharmacy_stocks(pharmacies, medications)
    create_notification_templates()

    # Створюємо тестове замовлення
    create_sample_order(users[0], medications, pharmacies[0])

    print("\n" + "=" * 60)
    print("✅ БАЗА ДАНИХ УСПІШНО НАПОВНЕНА!")
    print("=" * 60)
    print("\n📊 Статистика:")
    print(f"  👥 Користувачів: {User.objects.count()}")
    print(f"  🏥 Аптек: {Pharmacy.objects.count()}")
    print(f"  💊 Медикаментів: {Medication.objects.count()}")
    print(f"  📦 Залишків в аптеках: {PharmacyStock.objects.count()}")
    print(f"  🛒 Замовлень: {Order.objects.count()}")
    print("\n🔑 Дані для входу:")
    print("  Admin: username=admin, password=admin123")
    print("  User1: username=ivan_petrov, password=password123")
    print("  User2: username=maria_koval, password=password123")
    print("  User3: username=olga_shevchenko, password=password123")
    print()


if __name__ == '__main__':
    main()