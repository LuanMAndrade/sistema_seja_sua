"""
Tiny ERP API Integration for Finance Module
"""
import os
import requests
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TinyERPFinanceAPI:
    """
    Service for syncing finance data from Tiny ERP API
    """

    def __init__(self):
        self.api_token = os.getenv('TINY_ERP_API_TOKEN', '')
        self.api_url = os.getenv('TINY_ERP_API_URL', '')

        if not self.api_token or not self.api_url:
            logger.warning("Tiny ERP API credentials not configured in environment variables")

    def fetch_inflows(self):
        """
        Fetch financial inflows (revenue) from Tiny ERP API
        Returns list of dictionaries with inflow data
        """
        if not self.api_token or not self.api_url:
            logger.error("Cannot fetch inflows: API credentials not configured")
            return []

        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json',
            }

            # Adjust endpoint according to Tiny ERP API documentation
            endpoint = f"{self.api_url}/contas.receber.php"

            response = requests.get(endpoint, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Parse response according to Tiny ERP JSON format
            inflows = []

            if isinstance(data, dict) and 'retorno' in data:
                contas = data.get('retorno', {}).get('contas_receber', [])

                for item in contas:
                    conta = item.get('conta', {})
                    inflows.append({
                        'external_id': str(conta.get('id', '')),
                        'description': conta.get('descricao', ''),
                        'amount': Decimal(str(conta.get('valor', 0))),
                        'date': datetime.strptime(conta.get('data_vencimento', ''), '%d/%m/%Y').date() if conta.get('data_vencimento') else datetime.now().date(),
                        'sector_name': conta.get('categoria', ''),
                    })

            logger.info(f"Fetched {len(inflows)} inflows from Tiny ERP")
            return inflows

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching inflows from Tiny ERP: {e}")
            return []
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing Tiny ERP response: {e}")
            return []

    def fetch_outflows(self):
        """
        Fetch financial outflows (expenses) from Tiny ERP API
        Returns list of dictionaries with outflow data
        """
        if not self.api_token or not self.api_url:
            logger.error("Cannot fetch outflows: API credentials not configured")
            return []

        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json',
            }

            # Adjust endpoint according to Tiny ERP API documentation
            endpoint = f"{self.api_url}/contas.pagar.php"

            response = requests.get(endpoint, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Parse response according to Tiny ERP JSON format
            outflows = []

            if isinstance(data, dict) and 'retorno' in data:
                contas = data.get('retorno', {}).get('contas_pagar', [])

                for item in contas:
                    conta = item.get('conta', {})
                    outflows.append({
                        'external_id': str(conta.get('id', '')),
                        'description': conta.get('descricao', ''),
                        'amount': Decimal(str(conta.get('valor', 0))),
                        'date': datetime.strptime(conta.get('data_vencimento', ''), '%d/%m/%Y').date() if conta.get('data_vencimento') else datetime.now().date(),
                        'sector_name': conta.get('categoria', ''),
                    })

            logger.info(f"Fetched {len(outflows)} outflows from Tiny ERP")
            return outflows

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching outflows from Tiny ERP: {e}")
            return []
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing Tiny ERP response: {e}")
            return []

    def sync_inflow(self, inflow_data):
        """
        Sync a single inflow to the database
        Returns (inflow_object, created_flag)
        """
        from .models import FinanceInflow, FinanceSector

        try:
            # Get or create sector if sector_name is provided
            sector = None
            if inflow_data.get('sector_name'):
                sector, _ = FinanceSector.objects.get_or_create(
                    name=inflow_data['sector_name']
                )

            inflow, created = FinanceInflow.objects.update_or_create(
                external_id=inflow_data['external_id'],
                defaults={
                    'description': inflow_data['description'],
                    'amount': inflow_data['amount'],
                    'date': inflow_data['date'],
                    'sector': sector,
                }
            )
            return inflow, created
        except Exception as e:
            logger.error(f"Error syncing inflow {inflow_data.get('external_id')}: {e}")
            return None, False

    def sync_outflow(self, outflow_data):
        """
        Sync a single outflow to the database
        Returns (outflow_object, created_flag)
        """
        from .models import FinanceOutflow, FinanceSector

        try:
            # Get or create sector if sector_name is provided
            sector = None
            if outflow_data.get('sector_name'):
                sector, _ = FinanceSector.objects.get_or_create(
                    name=outflow_data['sector_name']
                )

            outflow, created = FinanceOutflow.objects.update_or_create(
                external_id=outflow_data['external_id'],
                defaults={
                    'description': outflow_data['description'],
                    'amount': outflow_data['amount'],
                    'date': outflow_data['date'],
                    'sector': sector,
                }
            )
            return outflow, created
        except Exception as e:
            logger.error(f"Error syncing outflow {outflow_data.get('external_id')}: {e}")
            return None, False

    def sync_all(self):
        """
        Fetch and sync all finance data from Tiny ERP
        Returns dict with statistics
        """
        # Sync inflows
        inflows_data = self.fetch_inflows()
        inflows_created = 0
        inflows_updated = 0
        inflows_errors = 0

        for inflow_data in inflows_data:
            inflow, created = self.sync_inflow(inflow_data)
            if inflow:
                if created:
                    inflows_created += 1
                else:
                    inflows_updated += 1
            else:
                inflows_errors += 1

        # Sync outflows
        outflows_data = self.fetch_outflows()
        outflows_created = 0
        outflows_updated = 0
        outflows_errors = 0

        for outflow_data in outflows_data:
            outflow, created = self.sync_outflow(outflow_data)
            if outflow:
                if created:
                    outflows_created += 1
                else:
                    outflows_updated += 1
            else:
                outflows_errors += 1

        logger.info(
            f"Finance sync completed: "
            f"Inflows ({inflows_created} created, {inflows_updated} updated, {inflows_errors} errors), "
            f"Outflows ({outflows_created} created, {outflows_updated} updated, {outflows_errors} errors)"
        )

        return {
            'inflows_created': inflows_created,
            'inflows_updated': inflows_updated,
            'inflows_errors': inflows_errors,
            'outflows_created': outflows_created,
            'outflows_updated': outflows_updated,
            'outflows_errors': outflows_errors,
        }
