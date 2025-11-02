from django.contrib import admin
from .models import Medication, MedicationReview


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'category', 'price', 'is_prescription', 'is_available']
    list_filter = ['category', 'is_prescription', 'is_available']
    search_fields = ['name', 'manufacturer', 'active_ingredient']
    list_editable = ['price', 'is_available']

    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'manufacturer', 'category', 'description')
        }),
        ('Медична інформація', {
            'fields': ('active_ingredient', 'dosage', 'is_prescription')
        }),
        ('Ціна та наявність', {
            'fields': ('price', 'is_available', 'image')
        }),
    )


@admin.register(MedicationReview)
class MedicationReviewAdmin(admin.ModelAdmin):
    list_display = ['medication', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['medication__name', 'user__username']