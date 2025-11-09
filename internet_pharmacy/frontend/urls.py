from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'frontend'

urlpatterns = [
    # Головна
    path('', views.index, name='index'),

    # Медикаменти
    path('medications/', views.medications_list, name='medications'),
    path('medications/<int:pk>/', views.medication_detail, name='medication_detail'),

    # Аптеки
    path('pharmacies/', views.pharmacies_list, name='pharmacies'),

    # Кошик
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),

    # Замовлення
    path('orders/', views.orders_list, name='orders'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),

    # Профіль
    path('profile/', views.profile_view, name='profile'),

    # Сповіщення
    path('notifications/', views.notifications_view, name='notifications'),

    # Авторизація
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='frontend/login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='frontend:index'
    ), name='logout'),  # ← ДОДАЛИ
]