"""
Tiny ERP Stock Synchronization for Store Collections
Syncs stock from Tiny ERP API directly to Collection Pieces using variation IDs
"""
import logging
from datetime import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)


class TinyERPStockSync:
    """
    Service for syncing stock from Tiny ERP API to Collection Pieces
    """

    def __init__(self):
        """Initialize with TinyERPSearch service for API calls"""
        from .tiny_search import TinyERPSearch
        self.tiny_search = TinyERPSearch()

    def sync_piece_stock(self, piece, record_history=True):
        """
        Sync stock for a single piece from Tiny ERP using its variation IDs
        Fetches fresh stock data from Tiny ERP API for each size
        Records stock history if there are changes

        Args:
            piece: Piece object to sync
            record_history: Whether to record stock changes in history (default True)

        Returns True if successful, False otherwise
        """
        if not piece.tiny_parent_id:
            logger.warning(f"Piece {piece.id} is not linked to any Tiny ERP product")
            return False

        try:
            # Check if piece has variation IDs
            has_variations = any([
                piece.tiny_variation_id_p,
                piece.tiny_variation_id_m,
                piece.tiny_variation_id_g,
                piece.tiny_variation_id_gg
            ])

            if not has_variations:
                logger.warning(f"Piece {piece.id} has no variation IDs configured")
                return False

            # Capture current stock before updating
            old_stock = {
                'P': piece.current_stock_p,
                'M': piece.current_stock_m,
                'G': piece.current_stock_g,
                'GG': piece.current_stock_gg,
            }

            # Fetch new stock for each size variation
            new_stock = {}

            if piece.tiny_variation_id_p:
                new_stock['P'] = self.tiny_search.get_variation_stock(piece.tiny_variation_id_p)
            else:
                new_stock['P'] = 0

            if piece.tiny_variation_id_m:
                new_stock['M'] = self.tiny_search.get_variation_stock(piece.tiny_variation_id_m)
            else:
                new_stock['M'] = 0

            if piece.tiny_variation_id_g:
                new_stock['G'] = self.tiny_search.get_variation_stock(piece.tiny_variation_id_g)
            else:
                new_stock['G'] = 0

            if piece.tiny_variation_id_gg:
                new_stock['GG'] = self.tiny_search.get_variation_stock(piece.tiny_variation_id_gg)
            else:
                new_stock['GG'] = 0

            # Update piece stock
            piece.current_stock_p = new_stock['P']
            piece.current_stock_m = new_stock['M']
            piece.current_stock_g = new_stock['G']
            piece.current_stock_gg = new_stock['GG']
            piece.stock_last_synced = timezone.now()

            piece.save(update_fields=[
                'current_stock_p',
                'current_stock_m',
                'current_stock_g',
                'current_stock_gg',
                'stock_last_synced'
            ])

            # Record history if enabled and there are changes
            if record_history:
                self._record_stock_history(piece, old_stock, new_stock)

            logger.info(
                f"Successfully synced stock for piece {piece.id} ({piece.collection.name}): "
                f"P={piece.current_stock_p}, M={piece.current_stock_m}, "
                f"G={piece.current_stock_g}, GG={piece.current_stock_gg}, "
                f"Total={piece.total_current_stock}"
            )
            return True

        except Exception as e:
            logger.error(f"Error syncing stock for piece {piece.id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def _record_stock_history(self, piece, old_stock, new_stock):
        """
        Record stock changes in history
        Only creates records when there is actual stock change

        Args:
            piece: Piece object
            old_stock: Dict with old stock values {'P': 10, 'M': 20, ...}
            new_stock: Dict with new stock values {'P': 8, 'M': 22, ...}
        """
        from .models import StockHistory

        sync_date = timezone.now()

        for size in ['P', 'M', 'G', 'GG']:
            old_value = old_stock[size]
            new_value = new_stock[size]

            # Only record if there's a change
            if old_value != new_value:
                difference = new_value - old_value

                # Determine movement type
                if old_value == 0 and new_value > 0:
                    movement_type = 'inicial'
                elif difference > 0:
                    movement_type = 'entrada'
                else:
                    movement_type = 'saida'

                # Create history record
                StockHistory.objects.create(
                    piece=piece,
                    size=size,
                    quantity=abs(difference),
                    movement_type=movement_type,
                    stock_after_movement=new_value,
                    date=sync_date
                )

                logger.info(
                    f"Stock history recorded: {piece.name} ({size}) - "
                    f"{movement_type} {abs(difference)} units, stock after: {new_value}"
                )

    def sync_all_pieces(self):
        """
        Sync stock for all pieces that are linked to Tiny ERP
        Returns (success_count, error_count)
        """
        from .models import Piece

        # Get all pieces that are linked to Tiny ERP (have parent ID)
        linked_pieces = Piece.objects.filter(tiny_parent_id__isnull=False).select_related('collection')

        success_count = 0
        error_count = 0

        for piece in linked_pieces:
            if self.sync_piece_stock(piece):
                success_count += 1
            else:
                error_count += 1

        logger.info(
            f"Stock sync completed: {success_count} successful, {error_count} errors, "
            f"Total linked pieces: {linked_pieces.count()}"
        )
        return success_count, error_count

    def sync_collection_stock(self, collection):
        """
        Sync stock for all pieces in a specific collection
        Returns (success_count, error_count)
        """
        pieces = collection.pieces.filter(tiny_parent_id__isnull=False)

        success_count = 0
        error_count = 0

        for piece in pieces:
            if self.sync_piece_stock(piece):
                success_count += 1
            else:
                error_count += 1

        logger.info(
            f"Stock sync for collection {collection.name}: "
            f"{success_count} successful, {error_count} errors"
        )
        return success_count, error_count
