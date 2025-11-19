from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import InventoryPiece, InventoryAccessory


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
