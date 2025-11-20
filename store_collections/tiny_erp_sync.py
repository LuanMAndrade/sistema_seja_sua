"""
Tiny ERP Stock Synchronization for Store Collections
Syncs stock from Tiny ERP InventoryPiece to Collection Pieces
"""
import logging
from datetime import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)


class TinyERPStockSync:
    """
    Service for syncing stock from Tiny ERP to Collection Pieces
    """

    def sync_piece_stock(self, piece):
        """
        Sync stock for a single piece from its linked Tiny ERP piece
        Uses variation stock if available, otherwise distributes equally
        Returns True if successful, False otherwise
        """
        if not piece.tiny_erp_piece:
            logger.warning(f"Piece {piece.id} is not linked to any Tiny ERP piece")
            return False

        try:
            tiny_piece = piece.tiny_erp_piece
            total_stock = tiny_piece.quantity

            # Check if Tiny ERP piece has variations with size-specific stock
            if tiny_piece.has_variations:
                # Use the mapped variation stock
                piece.current_stock_p = tiny_piece.stock_p
                piece.current_stock_m = tiny_piece.stock_m
                piece.current_stock_g = tiny_piece.stock_g
                piece.current_stock_gg = tiny_piece.stock_gg

                logger.info(
                    f"Using variation stock for piece {piece.id}: "
                    f"P:{piece.current_stock_p}, M:{piece.current_stock_m}, "
                    f"G:{piece.current_stock_g}, GG:{piece.current_stock_gg}"
                )
            else:
                # No variations, distribute stock equally across sizes
                stock_per_size = total_stock // 4
                remainder = total_stock % 4

                piece.current_stock_p = stock_per_size + (1 if remainder > 0 else 0)
                piece.current_stock_m = stock_per_size + (1 if remainder > 1 else 0)
                piece.current_stock_g = stock_per_size + (1 if remainder > 2 else 0)
                piece.current_stock_gg = stock_per_size + (1 if remainder > 3 else 0)

                logger.info(
                    f"Distributing stock equally for piece {piece.id}: "
                    f"Total={total_stock} -> P:{piece.current_stock_p}, "
                    f"M:{piece.current_stock_m}, G:{piece.current_stock_g}, "
                    f"GG:{piece.current_stock_gg}"
                )

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

        # Get all pieces that are linked to Tiny ERP
        linked_pieces = Piece.objects.filter(tiny_erp_piece__isnull=False).select_related('tiny_erp_piece')

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
        pieces = collection.pieces.filter(tiny_erp_piece__isnull=False).select_related('tiny_erp_piece')

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
