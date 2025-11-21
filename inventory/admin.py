from django.contrib import admin
from .models import InventoryAccessory, Packaging, Gift


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
