from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import InventoryAccessory
from store_collections.models import Collection, Piece


@login_required
def inventory_list(request):
    """List all collection pieces with stock information"""
    # Get all pieces with their stock information
    pieces = Piece.objects.select_related('collection', 'category', 'fabric').order_by('-stock_last_synced')

    context = {
        'pieces': pieces,
        'total_pieces': pieces.count(),
        'total_stock': sum(piece.total_current_stock for piece in pieces),
    }
    return render(request, 'inventory/inventory_list.html', context)


@login_required
def accessories_list(request):
    """List all inventory accessories"""
    accessories = InventoryAccessory.objects.all()

    context = {
        'accessories': accessories,
        'total_accessories': accessories.count(),
    }
    return render(request, 'inventory/accessories_list.html', context)


@login_required
def collection_pieces_stock(request):
    """List all collection pieces with stock by size"""
    collections = Collection.objects.all().prefetch_related('pieces').order_by('-created_at')

    # Calculate totals
    all_pieces = Piece.objects.all()
    total_stock = sum(piece.total_current_stock for piece in all_pieces)

    context = {
        'collections': collections,
        'total_collections': collections.count(),
        'total_pieces': all_pieces.count(),
        'total_stock': total_stock,
    }
    return render(request, 'inventory/collection_stock.html', context)


@login_required
def sync_stock(request):
    """Synchronize stock from Tiny ERP for all linked pieces"""
    if request.method == 'POST':
        from store_collections.tiny_erp_sync import TinyERPStockSync

        sync_service = TinyERPStockSync()
        success_count, error_count = sync_service.sync_all_pieces()

        if error_count == 0:
            messages.success(
                request,
                f'Estoque sincronizado com sucesso! {success_count} peças atualizadas.'
            )
        elif success_count > 0:
            messages.warning(
                request,
                f'Sincronização parcial: {success_count} peças atualizadas, {error_count} com erro.'
            )
        else:
            messages.error(
                request,
                f'Erro na sincronização: {error_count} peças falharam.'
            )

    return redirect('inventory:inventory_list')
