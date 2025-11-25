from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from collections import defaultdict
import math
from store_collections.models import Piece, Fabric, StockHistory


def statistics_dashboard(request):
    """
    Dashboard page for statistics with button to generate replenishment numbers
    """
    context = {
        'title': 'Estatísticas'
    }
    return render(request, 'sales_stats/dashboard.html', context)


def generate_replenishment(request):
    """
    Calculate replenishment quantities based on sales data from last 120 days
    """
    if request.method != 'POST':
        return redirect('sales_stats:dashboard')

    # Calculate date 120 days ago
    cutoff_date = timezone.now() - timedelta(days=120)

    # Get all sales (saida) from last 120 days
    sales = StockHistory.objects.filter(
        movement_type='saida',
        date__gte=cutoff_date
    ).select_related('piece', 'piece__fabric', 'piece__category')

    # Group sales by fabric
    fabric_sales = defaultdict(lambda: {
        'categories': defaultdict(lambda: {
            'sizes': defaultdict(int),
            'total': 0
        }),
        'total': 0
    })

    # Process sales data
    for sale in sales:
        fabric = sale.piece.fabric
        category = sale.piece.category
        size = sale.size
        quantity = sale.quantity

        fabric_sales[fabric]['categories'][category]['sizes'][size] += quantity
        fabric_sales[fabric]['categories'][category]['total'] += quantity
        fabric_sales[fabric]['total'] += quantity

    # Calculate percentages
    fabric_percentages = {}
    for fabric, data in fabric_sales.items():
        fabric_percentages[fabric] = {
            'categories': {}
        }

        for category, cat_data in data['categories'].items():
            cat_percentage = (cat_data['total'] / data['total']) * 100 if data['total'] > 0 else 0

            size_percentages = {}
            for size, size_total in cat_data['sizes'].items():
                size_percentages[size] = (size_total / cat_data['total']) * 100 if cat_data['total'] > 0 else 0

            fabric_percentages[fabric]['categories'][category] = {
                'percentage': cat_percentage,
                'sizes': size_percentages
            }

    # Calculate replenishment for each piece
    replenishment_data = defaultdict(lambda: defaultdict(int))
    fabric_consumption = defaultdict(Decimal)

    # Get all active pieces for replenishment
    active_pieces = Piece.objects.filter(active_for_replenishment=True).select_related('fabric', 'category')

    for piece in active_pieces:
        fabric = piece.fabric
        category = piece.category

        # Get consumption for each size
        consumptions = {
            'P': piece.fabric_consumption_p,
            'M': piece.fabric_consumption_m,
            'G': piece.fabric_consumption_g,
            'GG': piece.fabric_consumption_gg
        }

        # Get current stock for each size
        current_stocks = {
            'P': piece.current_stock_p,
            'M': piece.current_stock_m,
            'G': piece.current_stock_g,
            'GG': piece.current_stock_gg
        }

        # Get initial quantities for each size
        initial_quantities = {
            'P': piece.initial_quantity_p,
            'M': piece.initial_quantity_m,
            'G': piece.initial_quantity_g,
            'GG': piece.initial_quantity_gg
        }

        # Get sales for this piece in the period
        piece_sales = sales.filter(piece=piece)
        piece_sales_by_size = defaultdict(int)
        for sale in piece_sales:
            piece_sales_by_size[sale.size] += sale.quantity

        for size in ['P', 'M', 'G', 'GG']:
            if piece.launch_status == 'em_lancamento':
                # For "Em lançamento" pieces, replenish exactly the initial quantity
                needed = initial_quantities[size]
            else:
                # For "Lançada" pieces: minimum 5 + sales in period - current stock
                minimum_stock = 5
                sold_in_period = piece_sales_by_size[size]
                target_stock = minimum_stock + sold_in_period
                needed = max(0, target_stock - current_stocks[size])

            if needed > 0:
                replenishment_data[piece][size] = needed
                fabric_consumption[fabric] += consumptions[size] * Decimal(needed)

    # Calculate fabric rolls needed
    fabric_rolls = {}
    fabric_surplus = {}

    for fabric, total_m2_needed in fabric_consumption.items():
        # Calculate m² per roll: roll_weight_kg * yield_area_per_kg
        m2_per_roll = fabric.roll_weight_kg * fabric.yield_area_per_kg

        # Calculate number of rolls needed (rounded up)
        rolls_needed = math.ceil(total_m2_needed / m2_per_roll)

        # Calculate total m² available with rounded rolls
        total_m2_available = m2_per_roll * Decimal(rolls_needed)

        # Calculate surplus
        surplus = total_m2_available - total_m2_needed

        fabric_rolls[fabric] = rolls_needed
        fabric_surplus[fabric] = surplus

    # Distribute surplus fabric using percentages
    surplus_pieces = defaultdict(lambda: defaultdict(int))

    for fabric, surplus_m2 in fabric_surplus.items():
        if surplus_m2 <= 0 or fabric not in fabric_percentages:
            continue

        # Get pieces that are "Lançada" (surplus is not for "Em lançamento" pieces)
        launched_pieces = [p for p in active_pieces if p.fabric == fabric and p.launch_status == 'lancada']

        for piece in launched_pieces:
            category = piece.category

            if category not in fabric_percentages[fabric]['categories']:
                continue

            cat_percentage = fabric_percentages[fabric]['categories'][category]['percentage']

            consumptions = {
                'P': piece.fabric_consumption_p,
                'M': piece.fabric_consumption_m,
                'G': piece.fabric_consumption_g,
                'GG': piece.fabric_consumption_gg
            }

            for size in ['P', 'M', 'G', 'GG']:
                if size not in fabric_percentages[fabric]['categories'][category]['sizes']:
                    continue

                size_percentage = fabric_percentages[fabric]['categories'][category]['sizes'][size]

                # Calculate m² for this variation
                variation_m2 = surplus_m2 * Decimal(cat_percentage / 100) * Decimal(size_percentage / 100)

                # Calculate number of pieces (rounded to nearest integer)
                if consumptions[size] > 0:
                    pieces_count = round(float(variation_m2 / consumptions[size]))
                    if pieces_count > 0:
                        surplus_pieces[piece][size] = pieces_count

    # Combine replenishment and surplus
    final_replenishment = defaultdict(lambda: defaultdict(int))

    for piece, sizes in replenishment_data.items():
        for size, quantity in sizes.items():
            final_replenishment[piece][size] = quantity

    for piece, sizes in surplus_pieces.items():
        for size, quantity in sizes.items():
            final_replenishment[piece][size] += quantity

    # Convert defaultdict to regular dict for template compatibility
    final_replenishment_dict = {}
    for piece, sizes in final_replenishment.items():
        final_replenishment_dict[piece] = dict(sizes)

    # Calculate costs
    # 1. Fabric cost: price per roll × number of rolls
    fabric_cost = Decimal('0')
    for fabric, rolls in fabric_rolls.items():
        fabric_cost += fabric.price_per_roll * Decimal(rolls)

    # 2. Production cost: production cost per piece × total pieces
    production_cost = Decimal('0')
    total_pieces_count = 0
    for piece, sizes in final_replenishment_dict.items():
        piece_total = sum(sizes.values())
        total_pieces_count += piece_total
        production_cost += piece.category.production_cost_per_piece * Decimal(piece_total)

    # 3. Total cost
    total_cost = fabric_cost + production_cost

    context = {
        'title': 'Números de Reposição',
        'fabric_rolls': fabric_rolls,
        'pieces_replenishment': final_replenishment_dict,
        'fabric_cost': fabric_cost,
        'production_cost': production_cost,
        'total_cost': total_cost,
        'total_pieces_count': total_pieces_count
    }

    return render(request, 'sales_stats/replenishment_results.html', context)
