from django.contrib import admin
from .models import InventoryPiece, InventoryAccessory, Packaging, Gift


@admin.register(InventoryPiece)
class InventoryPieceAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'quantity', 'price', 'last_synced']
    search_fields = ['name', 'sku', 'external_id']
    list_filter = ['category', 'last_synced']
    readonly_fields = ['external_id', 'name', 'sku', 'category', 'quantity', 'price', 'last_synced', 'created_at']

    def has_add_permission(self, request):
        # Cannot add manually - data comes from API
        return False

    def has_delete_permission(self, request, obj=None):
        # Cannot delete manually - managed by API sync
        return False


@admin.register(InventoryAccessory)
class InventoryAccessoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'minimum_quantity', 'price', 'delivery_time_days', 'updated_at']
    search_fields = ['name']
    list_filter = ['created_at', 'updated_at']


@admin.register(Packaging)
class PackagingAdmin(admin.ModelAdmin):
    list_display = ['name', 'minimum_quantity', 'price', 'delivery_time_days', 'updated_at']
    search_fields = ['name']
    list_filter = ['created_at', 'updated_at']


@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = ['name', 'minimum_quantity', 'price', 'delivery_time_days', 'updated_at']
    search_fields = ['name']
    list_filter = ['created_at', 'updated_at']
