from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# Імпорт ViewSets
from medications.views import MedicationViewSet, MedicationReviewViewSet
from pharmacies.views import PharmacyViewSet, PharmacyStockViewSet
from orders.views import OrderViewSet, ShoppingCartViewSet
from users.views import UserViewSet

# Створюємо Router для автоматичної генерації URL
router = DefaultRouter()

# Реєструємо ViewSets
router.register(r'medications', MedicationViewSet, basename='medication')
router.register(r'reviews', MedicationReviewViewSet, basename='review')
router.register(r'pharmacies', PharmacyViewSet, basename='pharmacy')
router.register(r'stocks', PharmacyStockViewSet, basename='stock')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'cart', ShoppingCartViewSet, basename='cart')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # API
    path('api/', include(router.urls)),

    # API Authentication
    path('api-auth/', include('rest_framework.urls')),

    # API Documentation (Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Logout (глобальний)
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # Frontend
    path('', include('frontend.urls')),
]

# Медіа файли (зображення медикаментів)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)