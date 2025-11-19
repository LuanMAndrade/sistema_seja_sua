"""
Tiny ERP API Integration for Sales Statistics Module
"""
import os
import requests
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TinyERPSalesAPI:
    """
    Service for syncing sales data from Tiny ERP API
    """

    def __init__(self):
        self.api_token = os.getenv('TINY_ERP_API_TOKEN', '')
        self.api_url = os.getenv('TINY_ERP_API_URL', '')

        if not self.api_token or not self.api_url:
            logger.warning("Tiny ERP API credentials not configured in environment variables")

    def fetch_sales_data(self):
        """
        Fetch sales data from Tiny ERP API
        Returns list of dictionaries with sales data
        """
        if not self.api_token or not self.api_url:
            logger.error("Cannot fetch sales data: API credentials not configured")
            return []

        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json',
            }

            # Adjust endpoint according to Tiny ERP API documentation
            endpoint = f"{self.api_url}/pedidos.php"

            response = requests.get(endpoint, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Parse response according to Tiny ERP JSON format
            sales = []

            if isinstance(data, dict) and 'retorno' in data:
                pedidos = data.get('retorno', {}).get('pedidos', [])

                for item in pedidos:
                    pedido = item.get('pedido', {})
                    itens = pedido.get('itens', [])

                    for produto_item in itens:
                        produto = produto_item.get('item', {})

                        sales.append({
                            'external_id': f"{pedido.get('id', '')}_{produto.get('id_produto', '')}",
                            'sale_date': datetime.strptime(pedido.get('data_pedido', ''), '%d/%m/%Y').date() if pedido.get('data_pedido') else datetime.now().date(),
                            'piece_sku': produto.get('codigo', ''),
                            'piece_name': produto.get('descricao', ''),
                            'quantity_sold': int(produto.get('quantidade', 0)),
                            'unit_price': Decimal(str(produto.get('valor_unitario', 0))),
                            'total_amount': Decimal(str(produto.get('valor_total', 0))),
                        })

            logger.info(f"Fetched {len(sales)} sales records from Tiny ERP")
            return sales

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching sales data from Tiny ERP: {e}")
            return []
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing Tiny ERP response: {e}")
            return []

    def sync_sales_record(self, sales_data):
        """
        Sync a single sales record to the database
        Returns (sales_object, created_flag)
        """
        from .models import SalesData

        try:
            sale, created = SalesData.objects.update_or_create(
                external_id=sales_data['external_id'],
                defaults={
                    'sale_date': sales_data['sale_date'],
                    'piece_sku': sales_data['piece_sku'],
                    'piece_name': sales_data['piece_name'],
                    'quantity_sold': sales_data['quantity_sold'],
                    'unit_price': sales_data['unit_price'],
                    'total_amount': sales_data['total_amount'],
                }
            )
            return sale, created
        except Exception as e:
            logger.error(f"Error syncing sales record {sales_data.get('external_id')}: {e}")
            return None, False

    def sync_all(self):
        """
        Fetch and sync all sales data from Tiny ERP
        Returns (created_count, updated_count, error_count)
        """
        sales_data_list = self.fetch_sales_data()

        created_count = 0
        updated_count = 0
        error_count = 0

        for sales_data in sales_data_list:
            sale, created = self.sync_sales_record(sales_data)
            if sale:
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            else:
                error_count += 1

        logger.info(f"Sales sync completed: {created_count} created, {updated_count} updated, {error_count} errors")
        return created_count, updated_count, error_count
