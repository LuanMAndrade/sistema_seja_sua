from django.contrib import admin
from .models import (
    SalesData,
    PieceSalesStatistics,
    CollectionSalesStatistics,
    FabricSalesStatistics,
    SalesForecast
)


@admin.register(SalesData)
class SalesDataAdmin(admin.ModelAdmin):
    list_display = [
        'piece_name',
        'piece_sku',
        'sale_date',
        'quantity_sold',
        'unit_price',
        'total_amount',
        'last_synced'
    ]
    search_fields = ['piece_name', 'piece_sku', 'external_id']
    list_filter = ['sale_date', 'last_synced']
    readonly_fields = [
        'external_id',
        'sale_date',
        'piece_sku',
        'piece_name',
        'quantity_sold',
        'unit_price',
        'total_amount',
        'quantity_p',
        'quantity_m',
        'quantity_g',
        'quantity_gg',
        'last_synced',
        'created_at'
    ]
    date_hierarchy = 'sale_date'

    def has_add_permission(self, request):
        # Cannot add manually - data comes from API
        return False

    def has_delete_permission(self, request, obj=None):
        # Cannot delete manually - managed by API sync
        return False


@admin.register(PieceSalesStatistics)
class PieceSalesStatisticsAdmin(admin.ModelAdmin):
    list_display = [
        'piece',
        'total_units_sold',
        'total_revenue',
        'average_sale_price',
        'first_sale_date',
        'last_sale_date',
        'last_calculated'
    ]
    search_fields = ['piece__collection__name']
    list_filter = ['first_sale_date', 'last_sale_date', 'last_calculated']
    readonly_fields = ['last_calculated', 'created_at']
    date_hierarchy = 'last_sale_date'

    fieldsets = (
        ('Piece Information', {
            'fields': ('piece',)
        }),
        ('Sales Metrics', {
            'fields': ('total_units_sold', 'total_revenue', 'average_sale_price')
        }),
        ('Size Breakdown', {
            'fields': ('total_sold_p', 'total_sold_m', 'total_sold_g', 'total_sold_gg')
        }),
        ('Performance', {
            'fields': ('first_sale_date', 'last_sale_date', 'days_since_launch')
        }),
        ('Timestamps', {
            'fields': ('last_calculated', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CollectionSalesStatistics)
class CollectionSalesStatisticsAdmin(admin.ModelAdmin):
    list_display = [
        'collection',
        'total_units_sold',
        'total_revenue',
        'average_piece_price',
        'total_pieces_in_collection',
        'collection_launch_date',
        'last_calculated'
    ]
    search_fields = ['collection__name', 'best_selling_piece_name', 'worst_selling_piece_name']
    list_filter = ['collection_launch_date', 'last_calculated']
    readonly_fields = ['last_calculated', 'created_at']
    date_hierarchy = 'collection_launch_date'

    fieldsets = (
        ('Collection Information', {
            'fields': ('collection', 'collection_launch_date', 'total_pieces_in_collection')
        }),
        ('Sales Metrics', {
            'fields': ('total_units_sold', 'total_revenue', 'average_piece_price')
        }),
        ('Performance', {
            'fields': ('best_selling_piece_name', 'worst_selling_piece_name')
        }),
        ('Timestamps', {
            'fields': ('last_calculated', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FabricSalesStatistics)
class FabricSalesStatisticsAdmin(admin.ModelAdmin):
    list_display = [
        'fabric',
        'total_pieces_using_fabric',
        'total_units_sold',
        'total_fabric_consumed_kg',
        'total_revenue_generated',
        'last_calculated'
    ]
    search_fields = ['fabric__name', 'fabric__color']
    list_filter = ['last_calculated']
    readonly_fields = ['last_calculated', 'created_at']

    fieldsets = (
        ('Fabric Information', {
            'fields': ('fabric',)
        }),
        ('Usage Metrics', {
            'fields': ('total_pieces_using_fabric', 'total_units_sold', 'total_fabric_consumed_kg')
        }),
        ('Revenue', {
            'fields': ('total_revenue_generated',)
        }),
        ('Timestamps', {
            'fields': ('last_calculated', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SalesForecast)
class SalesForecastAdmin(admin.ModelAdmin):
    list_display = [
        'forecast_type',
        'target_name',
        'forecast_date',
        'predicted_units',
        'predicted_revenue',
        'confidence_level',
        'model_used',
        'created_at'
    ]
    search_fields = ['target_name', 'model_used', 'notes']
    list_filter = ['forecast_type', 'forecast_date', 'confidence_level', 'model_used']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'forecast_date'

    fieldsets = (
        ('Forecast Information', {
            'fields': ('forecast_type', 'target_name', 'forecast_date')
        }),
        ('Predictions', {
            'fields': (
                'predicted_units',
                'predicted_revenue',
                'confidence_interval_lower',
                'confidence_interval_upper',
                'confidence_level'
            )
        }),
        ('Methodology', {
            'fields': ('model_used', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
