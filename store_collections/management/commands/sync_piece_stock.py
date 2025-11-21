"""
Management command to sync stock from Tiny ERP to Collection Pieces
Syncs InventoryPiece stock to linked Pieces
"""
from django.core.management.base import BaseCommand
from store_collections.models import Piece
from store_collections.tiny_erp_sync import TinyERPStockSync
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync stock from Tiny ERP InventoryPieces to Collection Pieces"

    def add_arguments(self, parser):
        parser.add_argument(
            "--piece-id",
            type=int,
            help="Sync specific piece by ID",
        )
        parser.add_argument(
            "--collection-id",
            type=int,
            help="Sync all pieces in a specific collection",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Verbose output",
        )

    def handle(self, *args, **options):
        verbose = options.get("verbose", False)
        piece_id = options.get("piece_id")
        collection_id = options.get("collection_id")

        if verbose:
            logger.setLevel(logging.DEBUG)

        sync_service = TinyERPStockSync()

        if piece_id:
            self.stdout.write(f"Syncing piece ID: {piece_id}")
            self.sync_piece(sync_service, piece_id, verbose)
        elif collection_id:
            self.stdout.write(f"Syncing all pieces in collection ID: {collection_id}")
            self.sync_collection(sync_service, collection_id, verbose)
        else:
            self.stdout.write("Syncing all linked pieces...")
            self.sync_all_pieces(sync_service, verbose)

        self.stdout.write(self.style.SUCCESS("Stock sync completed!"))

    def sync_piece(self, sync_service, piece_id, verbose):
        try:
            piece = Piece.objects.select_related("collection", "category").get(pk=piece_id)
            if not piece.tiny_parent_id:
                self.stdout.write(self.style.ERROR(f"Piece {piece_id} is not linked to Tiny ERP"))
                return
            self.stdout.write(f"Syncing: {piece.collection.name} - {piece.category}")
            if sync_service.sync_piece_stock(piece):
                self.stdout.write(self.style.SUCCESS(f"Stock updated: P={piece.current_stock_p}, M={piece.current_stock_m}, G={piece.current_stock_g}, GG={piece.current_stock_gg}"))
            else:
                self.stdout.write(self.style.ERROR("Failed to sync"))
        except Piece.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Piece with ID {piece_id} not found"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))

    def sync_collection(self, sync_service, collection_id, verbose):
        from store_collections.models import Collection
        try:
            collection = Collection.objects.get(pk=collection_id)
            self.stdout.write(f"Syncing collection: {collection.name}")
            success_count, error_count = sync_service.sync_collection_stock(collection)
            self.stdout.write(self.style.SUCCESS(f"Collection sync completed: {success_count} success, {error_count} errors"))
        except Collection.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Collection with ID {collection_id} not found"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))

    def sync_all_pieces(self, sync_service, verbose):
        pieces = Piece.objects.filter(tiny_parent_id__isnull=False).select_related("collection", "category")
        total = pieces.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("No pieces linked to Tiny ERP found"))
            return
        self.stdout.write(f"Found {total} linked pieces to sync")
        success_count = 0
        error_count = 0
        for i, piece in enumerate(pieces, 1):
            self.stdout.write(f"[{i}/{total}] {piece.collection.name} - {piece.category}")
            if sync_service.sync_piece_stock(piece):
                self.stdout.write(self.style.SUCCESS(f"  P={piece.current_stock_p}, M={piece.current_stock_m}, G={piece.current_stock_g}, GG={piece.current_stock_gg}"))
                success_count += 1
            else:
                self.stdout.write(self.style.ERROR("  Failed"))
                error_count += 1
        self.stdout.write(self.style.SUCCESS(f"Stock sync completed: {success_count} success, {error_count} errors"))
