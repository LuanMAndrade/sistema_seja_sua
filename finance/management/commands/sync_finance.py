"""
Management command to sync finance data from Tiny ERP API
"""
from django.core.management.base import BaseCommand
from finance.tiny_erp import TinyERPFinanceAPI


class Command(BaseCommand):
    help = 'Sync finance data (inflows and outflows) from Tiny ERP API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)

        self.stdout.write(self.style.WARNING('Starting finance sync from Tiny ERP...'))

        api = TinyERPFinanceAPI()
        stats = api.sync_all()

        total_errors = stats['inflows_errors'] + stats['outflows_errors']

        if total_errors > 0:
            self.stdout.write(
                self.style.ERROR(f'Sync completed with {total_errors} errors')
            )
        else:
            self.stdout.write(self.style.SUCCESS('Sync completed successfully'))

        if verbose or total_errors > 0:
            self.stdout.write('\nInflows:')
            self.stdout.write(f"  Created: {stats['inflows_created']}")
            self.stdout.write(f"  Updated: {stats['inflows_updated']}")
            self.stdout.write(f"  Errors: {stats['inflows_errors']}")

            self.stdout.write('\nOutflows:')
            self.stdout.write(f"  Created: {stats['outflows_created']}")
            self.stdout.write(f"  Updated: {stats['outflows_updated']}")
            self.stdout.write(f"  Errors: {stats['outflows_errors']}")
