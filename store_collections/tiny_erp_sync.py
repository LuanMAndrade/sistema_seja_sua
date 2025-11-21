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

    def sync_piece_stock(self, piece):
        """
        Sync stock for a single piece from Tiny ERP using its variation IDs
        Fetches fresh stock data from Tiny ERP API for each size
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

            # Fetch stock for each size variation
            if piece.tiny_variation_id_p:
                piece.current_stock_p = self.tiny_search.get_variation_stock(piece.tiny_variation_id_p)
            else:
                piece.current_stock_p = 0

            if piece.tiny_variation_id_m:
                piece.current_stock_m = self.tiny_search.get_variation_stock(piece.tiny_variation_id_m)
            else:
                piece.current_stock_m = 0

            if piece.tiny_variation_id_g:
                piece.current_stock_g = self.tiny_search.get_variation_stock(piece.tiny_variation_id_g)
            else:
                piece.current_stock_g = 0

            if piece.tiny_variation_id_gg:
                piece.current_stock_gg = self.tiny_search.get_variation_stock(piece.tiny_variation_id_gg)
            else:
                piece.current_stock_gg = 0

            piece.stock_last_synced = timezone.now()
            piece.save(update_fields=[
                'current_stock_p',
                'current_stock_m',
                'current_stock_g',
                'current_stock_gg',
                'stock_last_synced'
            ])

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
