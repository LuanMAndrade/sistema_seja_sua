import os
import requests
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

TINY_ERP_API_TOKEN="7149b2b736292118f84a97e53d576039db73020c59ad83d377efcdf14090c606"
TINY_ERP_API_URL="https://api.tiny.com.br/api2"




def get_variation_stock(variation_id):
        """
        Get stock for a specific product variation using produto.obter.estoque.php

        Args:
            variation_id (str): Variation ID in Tiny ERP

        Returns:
            float: Stock quantity for the variation
        """
        

        try:
            endpoint = f"{TINY_ERP_API_URL}/produto.obter.estoque.php"

            params = {
                'token': TINY_ERP_API_TOKEN,
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
                estoque = float(produto.get('saldo', 0))

                logger.info(f"Variation {variation_id} stock: {estoque}")
                return estoque

            return 0

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching variation stock from Tiny ERP: {e}")
            return 0
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing Tiny ERP variation stock response: {e}")
            return 0
        
def map_size_variations(variations):
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
            estoque = int(get_variation_stock(variation_id))
            

            size_stock[variation_name] = estoque

        logger.info(f"Final mapped variation stock: {size_stock}")
        return size_stock


variacoes =[
        {
          "variacao": {
            "id": "902375435",
            "codigo": "125186",
            "preco": 75,
            "preco_promocional": 0,
            "grade": {
              "Tamanho": "P"
            }
          }
        },
        {
          "variacao": {
            "id": "902375438",
            "codigo": "125187",
            "preco": 75,
            "preco_promocional": 0,
            "grade": {
              "Tamanho": "M"
            }
          }
        },
        {
          "variacao": {
            "id": "902375441",
            "codigo": "125188",
            "preco": 75,
            "preco_promocional": 0,
            "grade": {
              "Tamanho": "G"
            }
          }
        },
        {
          "variacao": {
            "id": "902375444",
            "codigo": "125189",
            "preco": 75,
            "preco_promocional": 0,
            "grade": {
              "Tamanho": "GG"
            }
          }
        }
      ]

        
if __name__ == "__main__":
    resultado = map_size_variations(variacoes)
    #resultado = get_variation_stock(902375438)
    print(resultado)