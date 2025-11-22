"""
Management command to sync stock daily from Tiny ERP
Records stock history for all pieces with movements
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from store_collections.models import Piece
from store_collections.tiny_erp_sync import TinyERPStockSync
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sincronização diária de estoque do Tiny ERP com registro de histórico'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate sync without recording history',
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        dry_run = options.get('dry_run', False)

        if verbose:
            logger.setLevel(logging.DEBUG)

        start_time = timezone.now()
        self.stdout.write(f"[{start_time.strftime('%d/%m/%Y %H:%M:%S')}] Iniciando sincronização diária de estoque...")

        if dry_run:
            self.stdout.write(self.style.WARNING("⚠️  DRY RUN MODE - Histórico não será registrado"))

        # Get all pieces linked to Tiny ERP
        linked_pieces = Piece.objects.filter(
            tiny_parent_id__isnull=False
        ).select_related('collection', 'category')

        total_pieces = linked_pieces.count()

        if total_pieces == 0:
            self.stdout.write(self.style.WARNING("Nenhuma peça vinculada ao Tiny ERP encontrada"))
            return

        self.stdout.write(f"📦 Encontradas {total_pieces} peças vinculadas ao Tiny ERP")
        self.stdout.write("-" * 60)

        # Initialize sync service
        sync_service = TinyERPStockSync()

        success_count = 0
        error_count = 0
        movements_count = 0

        for i, piece in enumerate(linked_pieces, 1):
            try:
                self.stdout.write(
                    f"[{i}/{total_pieces}] {piece.name} ({piece.collection.name})"
                )

                # Sync with history recording (unless dry-run)
                record_history = not dry_run
                success = sync_service.sync_piece_stock(piece, record_history=record_history)

                if success:
                    success_count += 1

                    # Count movements in this sync (check if history was created)
                    if record_history:
                        # Get history records created in the last 5 seconds
                        recent_history = piece.stock_history.filter(
                            date__gte=timezone.now() - timezone.timedelta(seconds=5)
                        ).count()
                        if recent_history > 0:
                            movements_count += recent_history
                            self.stdout.write(
                                self.style.SUCCESS(f"  ✓ Sincronizado - {recent_history} movimentação(ões) registrada(s)")
                            )
                        else:
                            self.stdout.write(
                                self.style.SUCCESS(f"  ✓ Sincronizado - Sem alterações no estoque")
                            )
                    else:
                        self.stdout.write(self.style.SUCCESS(f"  ✓ Sincronizado (dry-run)"))

                else:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f"  ✗ Erro na sincronização"))

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"  ✗ Erro: {str(e)}"))
                if verbose:
                    import traceback
                    logger.error(traceback.format_exc())

        # Summary
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("📊 RESUMO DA SINCRONIZAÇÃO"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"✓ Sucesso: {success_count} peças")
        self.stdout.write(f"✗ Erros: {error_count} peças")

        if not dry_run:
            self.stdout.write(f"📝 Movimentações registradas: {movements_count}")

        self.stdout.write(f"⏱️  Tempo total: {duration:.2f} segundos")
        self.stdout.write(f"🕐 Finalizado em: {end_time.strftime('%d/%m/%Y %H:%M:%S')}")
        self.stdout.write("=" * 60)

        if error_count == 0:
            self.stdout.write(self.style.SUCCESS("\n✅ Sincronização concluída com sucesso!"))
        else:
            self.stdout.write(self.style.WARNING(f"\n⚠️  Sincronização concluída com {error_count} erro(s)"))
