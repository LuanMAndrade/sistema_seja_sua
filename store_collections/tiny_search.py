"""
Tiny ERP Product Search Service
Searches products in Tiny ERP API by name
"""
import os
import requests
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class TinyERPSearch:
    """
    Service for searching products in Tiny ERP API
    """

    def __init__(self):
        self.api_token = os.getenv('TINY_ERP_API_TOKEN', '')
        self.api_url = os.getenv('TINY_ERP_API_URL', 'https://api.tiny.com.br/api2')

        if not self.api_token:
            logger.warning("Tiny ERP API token not configured in environment variables")

    def search_products(self, search_term):
        """
        Search products in Tiny ERP by name
        Returns list of dictionaries with product data

        Args:
            search_term (str): Product name to search

        Returns:
            list: List of products matching the search term
        """
        if not self.api_token:
            logger.error("Cannot search products: API token not configured")
            return []

        try:
            # Endpoint correto para pesquisa de produtos
            endpoint = f"{self.api_url}/produtos.pesquisa.php"

            # Parâmetros da requisição
            params = {
                'token': self.api_token,
                'formato': 'json',
                'pesquisa': search_term
            }

            logger.info(f"Searching Tiny ERP for: '{search_term}'")

            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            products = []

            # Parse response according to Tiny ERP JSON format
            if isinstance(data, dict):
                retorno = data.get('retorno', {})

                # Check for API errors
                if 'codigo_erro' in retorno:
                    error_code = retorno.get('codigo_erro')
                    error_message = retorno.get('erro', 'Unknown error')
                    logger.error(f"Tiny ERP API error {error_code}: {error_message}")
                    return []

                # Get products from response
                produtos = retorno.get('produtos', [])

                for item in produtos:
                    produto = item.get('produto', {})
                    products.append({
                        'id': str(produto.get('id', '')),
                        'name': produto.get('nome', ''),
                        'sku': produto.get('codigo', ''),
                        'price': float(produto.get('preco', 0)),
                        'quantity': int(produto.get('saldo', 0)),
                        'unit': produto.get('unidade', ''),
                    })

            logger.info(f"Found {len(products)} products matching '{search_term}'")
            return products

        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching products in Tiny ERP: {e}")
            return []
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing Tiny ERP search response: {e}")
            return []

    def get_product_details(self, product_id):
        """
        Get detailed product information including variations from Tiny ERP

        Args:
            product_id (str): Product ID in Tiny ERP

        Returns:
            dict: Product details with variations
        """
        if not self.api_token:
            logger.error("Cannot get product details: API token not configured")
            return None

        try:
            endpoint = f"{self.api_url}/produto.obter.php"

            params = {
                'token': self.api_token,
                'formato': 'json',
                'id': product_id
            }

            logger.info(f"Fetching product details for ID: {product_id}")

            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if isinstance(data, dict):
                retorno = data.get('retorno', {})

                # Check for API errors
                if 'codigo_erro' in retorno:
                    error_code = retorno.get('codigo_erro')
                    error_message = retorno.get('erro', 'Unknown error')
                    logger.error(f"Tiny ERP API error {error_code}: {error_message}")
                    return None

                # Get product details
                produto = retorno.get('produto', {})
                return produto

            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching product details from Tiny ERP: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing Tiny ERP product details response: {e}")
            return None

    def get_variation_stock(self, variation_id):
        """
        Get stock for a specific product variation using produto.obter.estoque.php

        Args:
            variation_id (str): Variation ID in Tiny ERP

        Returns:
            float: Stock quantity for the variation
        """
        if not self.api_token:
            logger.error("Cannot get variation stock: API token not configured")
            return 0

        try:
            endpoint = f"{self.api_url}/produto.obter.estoque.php"

            params = {
                'token': self.api_token,
                'formato': 'json',
                'id': variation_id
            }

            logger.info(f"Fetching stock for variation ID: {variation_id}")

            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if isinstance(data, dict):
                retorno = data.get('retorno', {})

                # Check for API errors
                if 'codigo_erro' in retorno:
                    error_code = retorno.get('codigo_erro')
                    error_message = retorno.get('erro', 'Unknown error')
                    logger.error(f"Tiny ERP API error {error_code}: {error_message}")
                    return 0

                # Get stock information
                produto = retorno.get('produto', {})
                estoque = int(produto.get('saldo', 0))

                logger.info(f"Variation {variation_id} stock: {estoque}")
                return estoque

            return 0

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching variation stock from Tiny ERP: {e}")
            return 0
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing Tiny ERP variation stock response: {e}")
            return 0

    def map_size_variations(self, variations):
        """
        Map Tiny ERP variations to P, M, G, GG sizes
        Fetches accurate stock for each variation using produto.obter.estoque.php

        Args:
            variations (list): List of variations from Tiny ERP

        Returns:
            dict: Mapped stock by size {P: qty, M: qty, G: qty, GG: qty}
        """
        size_stock = {'P': 0, 'M': 0, 'G': 0, 'GG': 0}

        if not variations:
            return size_stock

        for variation in variations:
            variation = variation.get('variacao', {})
            grade = variation.get('grade', {})

            # Try to get variation name/size
            variation_name = grade.get('Tamanho', '').upper().strip()

            # Get variation ID for accurate stock lookup
            variation_id = variation.get('id')

            if not variation_id:
                logger.warning(f"Variation '{variation_name}' has no ID, skipping")
                continue

            # Fetch accurate stock for this variation using the dedicated endpoint
            estoque = self.get_variation_stock(variation_id)

            size_stock[variation_name] = estoque

        logger.info(f"Final mapped variation stock: {size_stock}")
        return size_stock

    def get_or_create_inventory_piece(self, product_data):
        """
        Get or create an InventoryPiece from product data
        Fetches product details including variations

        Args:
            product_data (dict): Product data from Tiny ERP search

        Returns:
            InventoryPiece: The created or existing inventory piece
        """
        from inventory.models import InventoryPiece

        try:
            product_id = product_data['id']

            # Fetch detailed product information with variations
            product_details = self.get_product_details(product_id)

            if not product_details:
                # Fallback to basic product data without variations
                logger.warning(f"Could not fetch details for product {product_id}, using basic data")
                product_details = {}

            # Get variations
            variacoes = product_details.get('variacoes', [])
            has_variations = len(variacoes) > 0

            # Map sizes
            size_stock = {'P': 0, 'M': 0, 'G': 0, 'GG': 0}
            total_quantity = product_data.get('quantity', 0)

            if has_variations:
                size_stock = self.map_size_variations(variacoes)
                total_quantity = sum(size_stock.values())
                logger.info(f"Product has {len(variacoes)} variations, total stock: {total_quantity}")
            else:
                # No variations, distribute equally or use total
                logger.info(f"Product has no variations, using total stock: {total_quantity}")

            # Create or update inventory piece
            piece, created = InventoryPiece.objects.update_or_create(
                external_id=product_id,
                defaults={
                    'name': product_data['name'],
                    'sku': product_data.get('sku', ''),
                    'category': product_details.get('tipo', ''),
                    'quantity': total_quantity,
                    'price': Decimal(str(product_data.get('price', 0))),
                    'has_variations': has_variations,
                    'stock_p': size_stock['P'],
                    'stock_m': size_stock['M'],
                    'stock_g': size_stock['G'],
                    'stock_gg': size_stock['GG'],
                    'variations_data': variacoes if has_variations else None,
                }
            )

            logger.info(
                f"{'Created' if created else 'Updated'} InventoryPiece: {piece.name} "
                f"(P:{piece.stock_p}, M:{piece.stock_m}, G:{piece.stock_g}, GG:{piece.stock_gg})"
            )
            return piece

        except Exception as e:
            logger.error(f"Error creating/updating InventoryPiece: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
