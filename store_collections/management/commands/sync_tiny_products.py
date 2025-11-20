"""
Management command to re-sync products from Tiny ERP
Updates InventoryPiece with latest stock and variations data
"""
from django.core.management.base import BaseCommand
from inventory.models import InventoryPiece
from store_collections.tiny_search import TinyERPSearch
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Re-sync products from Tiny ERP to update stock and variations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--product-id',
            type=str,
            help='Sync specific product by External ID',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output',
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        product_id = options.get('product_id')

        if verbose:
            logger.setLevel(logging.DEBUG)

        tiny_search = TinyERPSearch()

        if product_id:
            # Sync specific product
            self.stdout.write(f"Syncing product ID: {product_id}")
            self.sync_product(tiny_search, product_id, verbose)
        else:
            # Sync all existing products
            self.stdout.write("Syncing all existing products from Tiny ERP...")
            self.sync_all_products(tiny_search, verbose)

        self.stdout.write(self.style.SUCCESS("Sync completed!"))

    def sync_product(self, tiny_search, external_id, verbose):
        """Sync a single product by external ID"""
        try:
            piece = InventoryPiece.objects.get(external_id=external_id)

            # Fetch fresh data from Tiny ERP
            product_details = tiny_search.get_product_details(external_id)

            if not product_details:
                self.stdout.write(self.style.ERROR(f"Could not fetch details for product {external_id}"))
                return

            # Get variations
            variacoes = product_details.get('variacoes', [])
            has_variations = len(variacoes) > 0

            # Map sizes
            size_stock = {'P': 0, 'M': 0, 'G': 0, 'GG': 0}
            total_quantity = int(product_details.get('saldo', 0))

            if has_variations:
                size_stock = tiny_search.map_size_variations(variacoes)
                total_quantity = sum(size_stock.values())
                if verbose:
                    self.stdout.write(f"  Found {len(variacoes)} variations")
                    self.stdout.write(f"  Stock by size: P={size_stock['P']}, M={size_stock['M']}, G={size_stock['G']}, GG={size_stock['GG']}")

            # Update inventory piece
            piece.quantity = total_quantity
            piece.has_variations = has_variations
            piece.stock_p = size_stock['P']
            piece.stock_m = size_stock['M']
            piece.stock_g = size_stock['G']
            piece.stock_gg = size_stock['GG']
            piece.variations_data = variacoes if has_variations else None
            piece.save()

            self.stdout.write(self.style.SUCCESS(f"[OK] Updated: {piece.name} (Total: {total_quantity})"))

        except InventoryPiece.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Product with external_id {external_id} not found in database"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error syncing product {external_id}: {e}"))

    def sync_all_products(self, tiny_search, verbose):
        """Sync all existing InventoryPieces"""
        pieces = InventoryPiece.objects.all()
        total = pieces.count()

        self.stdout.write(f"Found {total} products to sync")

        success_count = 0
        error_count = 0

        for i, piece in enumerate(pieces, 1):
            self.stdout.write(f"[{i}/{total}] Syncing: {piece.name} (ID: {piece.external_id})")

            try:
                # Fetch fresh data from Tiny ERP
                product_details = tiny_search.get_product_details(piece.external_id)

                if not product_details:
                    self.stdout.write(self.style.WARNING(f"  [WARNING] Could not fetch details"))
                    error_count += 1
                    continue

                # Get variations
                variacoes = product_details.get('variacoes', [])
                has_variations = len(variacoes) > 0

                # Map sizes
                size_stock = {'P': 0, 'M': 0, 'G': 0, 'GG': 0}
                total_quantity = int(product_details.get('saldo', 0))

                if has_variations:
                    size_stock = tiny_search.map_size_variations(variacoes)
                    total_quantity = sum(size_stock.values())
                    if verbose:
                        self.stdout.write(f"  Found {len(variacoes)} variations")
                        self.stdout.write(f"  Stock: P={size_stock['P']}, M={size_stock['M']}, G={size_stock['G']}, GG={size_stock['GG']}")

                # Update inventory piece
                piece.quantity = total_quantity
                piece.has_variations = has_variations
                piece.stock_p = size_stock['P']
                piece.stock_m = size_stock['M']
                piece.stock_g = size_stock['G']
                piece.stock_gg = size_stock['GG']
                piece.variations_data = variacoes if has_variations else None
                piece.save()

                self.stdout.write(self.style.SUCCESS(f"  [OK] Updated (Total: {total_quantity})"))
                success_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  [ERROR] Error: {e}"))
                error_count += 1

        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(f"Sync completed: {success_count} success, {error_count} errors"))
