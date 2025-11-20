from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Collection, Piece
from calendar_app.models import CalendarEvent


def calculate_collection_dates(collection):
    """
    Calculate all milestone dates for a collection based on launch date.
    Works backward from expected_launch_date or actual_launch_date.
    """
    if not collection.expected_launch_date and not collection.actual_launch_date:
        return None

    launch_date = collection.actual_launch_date or collection.expected_launch_date

    # Calculate dates backward from launch
    dates = {}
    current_date = launch_date

    # Transportation (last phase before launch)
    transportation_start = current_date - timedelta(days=collection.transportation_time)
    dates['transportation'] = (transportation_start, current_date)
    current_date = transportation_start

    # Preparation
    preparation_start = current_date - timedelta(days=collection.preparation_time)
    dates['preparation'] = (preparation_start, current_date)
    current_date = preparation_start

    # Production
    production_start = current_date - timedelta(days=collection.production_time)
    dates['production'] = (production_start, current_date)
    current_date = production_start

    # Test piece
    test_piece_start = current_date - timedelta(days=collection.test_piece_time)
    dates['test_piece'] = (test_piece_start, current_date)
    current_date = test_piece_start

    # Pilot piece
    pilot_piece_start = current_date - timedelta(days=collection.pilot_piece_time)
    dates['pilot_piece'] = (pilot_piece_start, current_date)
    current_date = pilot_piece_start

    # Modeling
    modeling_start = current_date - timedelta(days=collection.modeling_time)
    dates['modeling'] = (modeling_start, current_date)

    # Launch event
    dates['launch'] = (launch_date, launch_date)

    return dates


@receiver(post_save, sender=Collection)
def collection_saved(sender, instance, created, **kwargs):
    """
    Triggered when a Collection is saved.
    Creates or updates calendar events for collection milestones.
    """
    # Only create events if we have launch dates
    if not instance.expected_launch_date and not instance.actual_launch_date:
        return

    dates = calculate_collection_dates(instance)
    if not dates:
        return

    # Event type configurations
    event_configs = [
        ('modeling', 'Modelagem', f'Modelagem da coleção {instance.name}'),
        ('pilot_piece', 'Peça Piloto', f'Peça piloto da coleção {instance.name}'),
        ('test_piece', 'Peça Teste', f'Peça teste para produção - {instance.name}'),
        ('production', 'Produção', f'Produção da coleção {instance.name}'),
        ('preparation', 'Preparação', f'Preparação da coleção {instance.name}'),
        ('transportation', 'Transporte', f'Transporte da coleção {instance.name}'),
        ('launch', 'Lançamento', f'Lançamento da coleção {instance.name}'),
    ]

    for event_type, title, description in event_configs:
        if event_type not in dates:
            continue

        start_date, end_date = dates[event_type]

        # Check if event already exists for this collection and type
        event, event_created = CalendarEvent.objects.get_or_create(
            collection=instance,
            event_type=event_type,
            defaults={
                'title': title,
                'description': description,
                'start_date': start_date,
                'end_date': end_date if start_date != end_date else None,
                'all_day': True,
                'sync_enabled': True,
            }
        )

        # Update existing event if dates changed
        if not event_created:
            event.title = title
            event.description = description
            event.start_date = start_date
            event.end_date = end_date if start_date != end_date else None
            event.save()


@receiver(pre_delete, sender=Collection)
def collection_deleted(sender, instance, **kwargs):
    """
    When a collection is deleted, delete all associated calendar events.
    """
    CalendarEvent.objects.filter(
        collection=instance,
        event_type__in=['modeling', 'pilot_piece', 'test_piece', 'production', 'preparation', 'transportation', 'launch']
    ).delete()


@receiver(post_save, sender=Piece)
def piece_saved(sender, instance, created, **kwargs):
    """
    Triggered when a Piece is saved.
    Update collection statistics and finance predictions.
    Sync stock from Tiny ERP if piece is linked.
    """
    # Import here to avoid circular imports
    from sales_stats.models import PieceSalesStatistics, CollectionSalesStatistics
    from .tiny_erp_sync import TinyERPStockSync

    # Get the fields that were updated
    update_fields = kwargs.get('update_fields')

    # Sync stock from Tiny ERP if piece is linked
    # Only sync if this is not already a stock sync update (to avoid loops)
    stock_sync_fields = {'current_stock_p', 'current_stock_m', 'current_stock_g', 'current_stock_gg', 'stock_last_synced'}
    is_stock_sync_update = update_fields is not None and set(update_fields) == stock_sync_fields

    if instance.tiny_erp_piece and not is_stock_sync_update:
        # Sync immediately after linking or when piece is updated
        sync_service = TinyERPStockSync()
        sync_service.sync_piece_stock(instance)

    # Create or update piece statistics if it doesn't exist
    if created:
        PieceSalesStatistics.objects.get_or_create(
            piece=instance,
            defaults={
                'total_units_sold': 0,
                'total_revenue': 0,
                'average_sale_price': instance.sale_price,
            }
        )

    # Update collection statistics
    collection = instance.collection
    pieces_count = collection.pieces.count()

    collection_stats, stats_created = CollectionSalesStatistics.objects.get_or_create(
        collection=collection,
        defaults={
            'total_pieces_in_collection': pieces_count,
            'collection_launch_date': collection.actual_launch_date or collection.expected_launch_date,
        }
    )

    if not stats_created:
        collection_stats.total_pieces_in_collection = pieces_count
        collection_stats.save()
