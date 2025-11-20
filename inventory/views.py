from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import InventoryPiece, InventoryAccessory
from store_collections.models import Collection, Piece


@login_required
def inventory_list(request):
    """List all inventory pieces from Tiny ERP"""
    pieces = InventoryPiece.objects.all().order_by('-last_synced')

    context = {
        'pieces': pieces,
        'total_pieces': pieces.count(),
        'total_quantity': sum(piece.quantity for piece in pieces),
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
