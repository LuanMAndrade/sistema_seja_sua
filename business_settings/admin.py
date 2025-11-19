from django.contrib import admin
from .models import Supplier, PieceCategory, BusinessDeadlines


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'delivery_time_days', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(PieceCategory)
class PieceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'subcategory', 'created_at']
    search_fields = ['name', 'subcategory']
    list_filter = ['created_at']


@admin.register(BusinessDeadlines)
class BusinessDeadlinesAdmin(admin.ModelAdmin):
    list_display = [
        'production_time',
        'fabric_testing_time',
        'modeling_time',
        'pilot_piece_time',
        'updated_at'
    ]

    def has_add_permission(self, request):
        # Only allow one instance
        return not BusinessDeadlines.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False
