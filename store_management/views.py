from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from store_collections.models import Collection, Piece
from inventory.models import InventoryAccessory
from finance.models import FinanceInflow, FinanceOutflow
from calendar_app.models import CalendarEvent
from sales_stats.models import SalesData, SalesForecast
from marketing.models import MarketingCampaign, SocialMediaPost
from notes.models import Note


@login_required
def home(request):
    """
    Home page view with dashboard statistics
    """
    # Get counts for all modules
    context = {
        # Collections
        'collections_count': Collection.objects.count(),
        'pieces_count': Piece.objects.count(),

        # Inventory
        'inventory_pieces_count': Piece.objects.filter(tiny_parent_id__isnull=False).count(),
        'inventory_accessories_count': InventoryAccessory.objects.count(),

        # Finance
        'inflows_count': FinanceInflow.objects.count(),
        'outflows_count': FinanceOutflow.objects.count(),

        # Calendar
        'upcoming_events_count': CalendarEvent.objects.filter(
            start_date__gte=timezone.now().date(),
            start_date__lte=timezone.now().date() + timedelta(days=30)
        ).count(),
        'total_events_count': CalendarEvent.objects.count(),

        # Statistics
        'sales_data_count': SalesData.objects.count(),
        'forecasts_count': SalesForecast.objects.count(),

        # Marketing
        'campaigns_count': MarketingCampaign.objects.count(),
        'social_posts_count': SocialMediaPost.objects.count(),

        # Notes
        'notes_count': Note.objects.count(),
    }

    return render(request, 'home.html', context)
