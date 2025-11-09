from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from medications.models import Medication
from pharmacies.models import Pharmacy
from orders.models import Order, ShoppingCart
from users.models import User


def index(request):
    """Головна сторінка"""
    pharmacies_count = Pharmacy.objects.filter(is_active=True).count()

    context = {
        'pharmacies_count': pharmacies_count,
    }
    return render(request, 'frontend/index.html', context)


def medications_list(request):
    """Список медикаментів"""
    return render(request, 'frontend/medications/list.html')


def medication_detail(request, pk):
    """Деталі медикаменту"""
    medication = get_object_or_404(Medication, pk=pk)

    context = {
        'medication': medication,
    }
    return render(request, 'frontend/medications/detail.html', context)


def pharmacies_list(request):
    """Список аптек"""
    return render(request, 'frontend/pharmacies.html')


@login_required
def cart_view(request):
    """Кошик"""
    return render(request, 'frontend/cart.html')


@login_required
def orders_list(request):
    """Список замовлень користувача"""
    return render(request, 'frontend/orders/list.html')


@login_required
def order_detail(request, pk):
    """Деталі замовлення"""
    order = get_object_or_404(Order, pk=pk, user=request.user)

    context = {
        'order': order,
    }
    return render(request, 'frontend/orders/detail.html', context)


@login_required
def profile_view(request):
    """Профіль користувача"""
    return render(request, 'frontend/profile.html')


def register_view(request):
    """Реєстрація"""
    if request.user.is_authenticated:
        return redirect('frontend:index')

    return render(request, 'frontend/register.html')


@login_required
def notifications_view(request):
    """Сповіщення користувача"""
    return render(request, 'frontend/notifications.html')


@login_required
@require_http_methods(["POST"])
def add_to_cart(request):
    """Додати товар в кошик (AJAX)"""
    medication_id = request.POST.get('medication_id')
    quantity = int(request.POST.get('quantity', 1))

    try:
        medication = Medication.objects.get(id=medication_id)
        cart, created = ShoppingCart.objects.get_or_create(user=request.user)
        cart.add_item(medication, quantity)

        return JsonResponse({
            'success': True,
            'message': f'{medication.name} додано до кошика',
            'cart_count': cart.get_items_count()
        })
    except Medication.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Медикамент не знайдено'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)