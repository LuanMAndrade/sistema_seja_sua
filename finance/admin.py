from django.contrib import admin
from .models import FinanceSector, FinanceInflow, FinanceOutflow, PredictedExpense


@admin.register(FinanceSector)
class FinanceSectorAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at', 'updated_at']


@admin.register(FinanceInflow)
class FinanceInflowAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'date', 'sector', 'last_synced']
    search_fields = ['description', 'external_id']
    list_filter = ['sector', 'date', 'last_synced']
    readonly_fields = ['external_id', 'description', 'amount', 'date', 'sector', 'last_synced', 'created_at']
    date_hierarchy = 'date'

    def has_add_permission(self, request):
        # Cannot add manually - data comes from API
        return False

    def has_delete_permission(self, request, obj=None):
        # Cannot delete manually - managed by API sync
        return False


@admin.register(FinanceOutflow)
class FinanceOutflowAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'date', 'sector', 'last_synced']
    search_fields = ['description', 'external_id']
    list_filter = ['sector', 'date', 'last_synced']
    readonly_fields = ['external_id', 'description', 'amount', 'date', 'sector', 'last_synced', 'created_at']
    date_hierarchy = 'date'

    def has_add_permission(self, request):
        # Cannot add manually - data comes from API
        return False

    def has_delete_permission(self, request, obj=None):
        # Cannot delete manually - managed by API sync
        return False


@admin.register(PredictedExpense)
class PredictedExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'predicted_amount', 'predicted_date', 'sector', 'confidence_level', 'updated_at']
    search_fields = ['description', 'notes']
    list_filter = ['sector', 'predicted_date', 'confidence_level']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'predicted_date'
    fieldsets = (
        ('Prediction Information', {
            'fields': ('description', 'predicted_amount', 'predicted_date', 'sector')
        }),
        ('Confidence & Notes', {
            'fields': ('confidence_level', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
