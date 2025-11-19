"""
Management command to sync sales data from Tiny ERP API
"""
from django.core.management.base import BaseCommand
from sales_stats.tiny_erp import TinyERPSalesAPI


class Command(BaseCommand):
    help = 'Sync sales data from Tiny ERP API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)

        self.stdout.write(self.style.WARNING('Starting sales data sync from Tiny ERP...'))

        api = TinyERPSalesAPI()
        created, updated, errors = api.sync_all()

        if errors > 0:
            self.stdout.write(
                self.style.ERROR(
                    f'Sync completed with errors: {created} created, {updated} updated, {errors} errors'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Sync completed successfully: {created} created, {updated} updated'
                )
            )

        if verbose:
            self.stdout.write(f'Created: {created}')
            self.stdout.write(f'Updated: {updated}')
            self.stdout.write(f'Errors: {errors}')
