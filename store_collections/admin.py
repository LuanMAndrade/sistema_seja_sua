from django.contrib import admin
from .models import Fabric, Collection, Piece, PieceColor, PieceImage


@admin.register(Fabric)
class FabricAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'supplier', 'roll_weight_kg', 'yield_area_per_kg']
    search_fields = ['name', 'color']
    list_filter = ['supplier', 'created_at']


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
        'name', 'category', 'fabric', 'status', 'sale_price', 'total_cost',
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
    list_display = ['name', 'collection', 'category', 'fabric', 'status', 'sale_price', 'total_cost', 'margin',
                    'is_synced_with_tiny', 'total_current_stock', 'stock_last_synced']
    search_fields = ['name', 'collection__name', 'category__name']
    list_filter = ['status', 'collection', 'category', 'created_at']
    inlines = [PieceColorInline, PieceImageInline]
    filter_horizontal = ['accessories']
    actions = ['sync_stock_from_tiny']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'collection', 'category', 'fabric', 'status')
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
        ('Tiny ERP Integration', {
            'fields': (
                'tiny_parent_id',
                ('tiny_variation_id_p', 'tiny_variation_id_m'),
                ('tiny_variation_id_g', 'tiny_variation_id_gg'),
            ),
            'description': 'IDs do produto e variações no Tiny ERP para sincronização de estoque.'
        }),
        ('Current Stock (Synced from Tiny ERP)', {
            'fields': (
                ('current_stock_p', 'current_stock_m'),
                ('current_stock_g', 'current_stock_gg'),
                'stock_last_synced',
            ),
            'classes': ('collapse',),
            'description': 'Estoque atual sincronizado do Tiny ERP. Use a ação "Sincronizar estoque do Tiny ERP" para atualizar.'
        }),
        ('Accessories', {
            'fields': ('accessories',)
        }),
    )

    readonly_fields = ['current_stock_p', 'current_stock_m', 'current_stock_g',
                       'current_stock_gg', 'stock_last_synced']

    def margin(self, obj):
        return f"{obj.margin:.2f}%"
    margin.short_description = 'Margin'

    def is_synced_with_tiny(self, obj):
        return obj.is_synced_with_tiny
    is_synced_with_tiny.boolean = True
    is_synced_with_tiny.short_description = 'Synced with Tiny'

    def sync_stock_from_tiny(self, request, queryset):
        """Admin action to sync stock from Tiny ERP for selected pieces"""
        from .tiny_erp_sync import TinyERPStockSync

        sync_service = TinyERPStockSync()
        success_count = 0
        error_count = 0

        for piece in queryset:
            if piece.tiny_parent_id:
                if sync_service.sync_piece_stock(piece):
                    success_count += 1
                else:
                    error_count += 1
            else:
                error_count += 1

        if success_count > 0:
            self.message_user(
                request,
                f'Estoque sincronizado com sucesso para {success_count} peça(s).',
                level='success'
            )
        if error_count > 0:
            self.message_user(
                request,
                f'Falha ao sincronizar {error_count} peça(s). Certifique-se de que estão vinculadas ao Tiny ERP.',
                level='warning'
            )

    sync_stock_from_tiny.short_description = 'Sincronizar estoque do Tiny ERP'


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
