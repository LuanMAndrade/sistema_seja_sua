from django.contrib import admin
from .models import Fabric, Accessory, Collection, Piece, PieceColor, PieceImage


@admin.register(Fabric)
class FabricAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'supplier', 'roll_weight_kg', 'yield_area_per_kg']
    search_fields = ['name', 'color']
    list_filter = ['supplier', 'created_at']


@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


class PieceColorInline(admin.TabularInline):
    model = PieceColor
    extra = 1


class PieceImageInline(admin.TabularInline):
    model = PieceImage
    extra = 0


class PieceInline(admin.StackedInline):
    model = Piece
    extra = 0
    fields = [
        'category', 'fabric', 'status', 'sale_price', 'total_cost',
        ('fabric_consumption_p', 'fabric_consumption_m', 'fabric_consumption_g', 'fabric_consumption_gg'),
        ('initial_quantity_p', 'initial_quantity_m', 'initial_quantity_g', 'initial_quantity_gg'),
        'accessories'
    ]
    filter_horizontal = ['accessories']


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'expected_launch_date', 'actual_launch_date', 'created_at']
    search_fields = ['name', 'notes']
    list_filter = ['status', 'created_at']
    inlines = [PieceInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'status', 'notes')
        }),
        ('Launch Dates', {
            'fields': ('expected_launch_date', 'actual_launch_date')
        }),
        ('Production Deadlines', {
            'fields': (
                'modeling_time',
                'pilot_piece_time',
                'test_piece_time',
                'production_time',
                'preparation_time',
                'transportation_time'
            )
        }),
    )


@admin.register(Piece)
class PieceAdmin(admin.ModelAdmin):
    list_display = ['collection', 'category', 'fabric', 'status', 'sale_price', 'total_cost', 'margin']
    search_fields = ['collection__name', 'category__name']
    list_filter = ['status', 'collection', 'category', 'created_at']
    inlines = [PieceColorInline, PieceImageInline]
    filter_horizontal = ['accessories']

    fieldsets = (
        ('Basic Information', {
            'fields': ('collection', 'category', 'fabric', 'status')
        }),
        ('Pricing', {
            'fields': ('sale_price', 'total_cost')
        }),
        ('Fabric Consumption (per size)', {
            'fields': (
                ('fabric_consumption_p', 'fabric_consumption_m'),
                ('fabric_consumption_g', 'fabric_consumption_gg'),
            )
        }),
        ('Initial Quantities (per size)', {
            'fields': (
                ('initial_quantity_p', 'initial_quantity_m'),
                ('initial_quantity_g', 'initial_quantity_gg'),
            )
        }),
        ('Accessories', {
            'fields': ('accessories',)
        }),
    )

    def margin(self, obj):
        return f"{obj.margin:.2f}%"
    margin.short_description = 'Margin'


@admin.register(PieceColor)
class PieceColorAdmin(admin.ModelAdmin):
    list_display = ['piece', 'color_name', 'color_hex']
    search_fields = ['piece__collection__name', 'color_name']
    list_filter = ['piece__collection']


@admin.register(PieceImage)
class PieceImageAdmin(admin.ModelAdmin):
    list_display = ['piece', 'caption', 'uploaded_at']
    search_fields = ['piece__collection__name', 'caption']
    list_filter = ['uploaded_at']
