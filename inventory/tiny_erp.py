"""
Tiny ERP API Integration for Inventory Module
"""
import os
import requests
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TinyERPInventoryAPI:
    """
    Service for syncing inventory data from Tiny ERP API
    """

    def __init__(self):
        self.api_token = os.getenv('TINY_ERP_API_TOKEN', '')
        self.api_url = os.getenv('TINY_ERP_API_URL', '')

        if not self.api_token or not self.api_url:
            logger.warning("Tiny ERP API credentials not configured in environment variables")

    def fetch_inventory_pieces(self):
        """
        Fetch inventory pieces from Tiny ERP API
        Returns list of dictionaries with piece data
        """
        if not self.api_token or not self.api_url:
            logger.error("Cannot fetch inventory: API credentials not configured")
            return []

        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json',
            }

            # Adjust endpoint according to Tiny ERP API documentation
            endpoint = f"{self.api_url}/produtos.php"

            response = requests.get(endpoint, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Parse response according to Tiny ERP JSON format
            # This is a placeholder - adjust according to actual API response structure
            pieces = []

            if isinstance(data, dict) and 'retorno' in data:
                produtos = data.get('retorno', {}).get('produtos', [])

                for item in produtos:
                    produto = item.get('produto', {})
                    pieces.append({
                        'external_id': str(produto.get('id', '')),
                        'name': produto.get('nome', ''),
                        'sku': produto.get('codigo', ''),
                        'category': produto.get('categoria', ''),
                        'quantity': int(produto.get('estoque_atual', 0)),
                        'price': Decimal(str(produto.get('preco', 0))),
                    })

            logger.info(f"Fetched {len(pieces)} inventory pieces from Tiny ERP")
            return pieces

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching inventory from Tiny ERP: {e}")
            return []
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing Tiny ERP response: {e}")
            return []

    def sync_inventory_piece(self, piece_data):
        """
        Sync a single inventory piece to the database
        Returns (piece_object, created_flag)
        """
        from .models import InventoryPiece

        try:
            piece, created = InventoryPiece.objects.update_or_create(
                external_id=piece_data['external_id'],
                defaults={
                    'name': piece_data['name'],
                    'sku': piece_data.get('sku', ''),
                    'category': piece_data.get('category', ''),
                    'quantity': piece_data.get('quantity', 0),
                    'price': piece_data.get('price', Decimal('0.00')),
                }
            )
            return piece, created
        except Exception as e:
            logger.error(f"Error syncing inventory piece {piece_data.get('external_id')}: {e}")
            return None, False

    def sync_all(self):
        """
        Fetch and sync all inventory pieces from Tiny ERP
        Returns (created_count, updated_count, error_count)
        """
        pieces_data = self.fetch_inventory_pieces()

        created_count = 0
        updated_count = 0
        error_count = 0

        for piece_data in pieces_data:
            piece, created = self.sync_inventory_piece(piece_data)
            if piece:
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            else:
                error_count += 1

        logger.info(f"Inventory sync completed: {created_count} created, {updated_count} updated, {error_count} errors")
        return created_count, updated_count, error_count
