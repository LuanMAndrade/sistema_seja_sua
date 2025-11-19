"""
Management command to sync inventory from Tiny ERP API
"""
from django.core.management.base import BaseCommand
from inventory.tiny_erp import TinyERPInventoryAPI


class Command(BaseCommand):
    help = 'Sync inventory pieces from Tiny ERP API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)

        self.stdout.write(self.style.WARNING('Starting inventory sync from Tiny ERP...'))

        api = TinyERPInventoryAPI()
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
