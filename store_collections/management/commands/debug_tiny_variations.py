"""
Management command to debug Tiny ERP variations
Usage:
    python manage.py debug_tiny_variations --search "nome_produto"
    python manage.py debug_tiny_variations --id "12345"
"""
from django.core.management.base import BaseCommand
from store_collections.tiny_search import TinyERPSearch
import json


class Command(BaseCommand):
    help = 'Debug Tiny ERP product variations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--search',
            type=str,
            help='Search for products by name',
        )
        parser.add_argument(
            '--id',
            type=str,
            help='Get product details by ID',
        )

    def handle(self, *args, **options):
        search_term = options.get('search')
        product_id = options.get('id')

        tiny_search = TinyERPSearch()

        if search_term:
            self.stdout.write(self.style.WARNING(f'\n=== Buscando produtos: "{search_term}" ===\n'))

            products = tiny_search.search_products(search_term)

            if not products:
                self.stdout.write(self.style.ERROR('Nenhum produto encontrado'))
                return

            self.stdout.write(self.style.SUCCESS(f'Encontrados {len(products)} produtos:\n'))

            for i, product in enumerate(products, 1):
                self.stdout.write(f'{i}. {product["name"]}')
                self.stdout.write(f'   ID: {product["id"]}')
                self.stdout.write(f'   SKU: {product["sku"]}')
                self.stdout.write(f'   Quantidade: {product["quantity"]}')
                self.stdout.write(f'   Preço: R$ {product["price"]:.2f}')
                self.stdout.write('')

            # Get details of first product
            if products:
                first_product_id = products[0]['id']
                self.stdout.write(self.style.WARNING(f'\n=== Buscando detalhes do primeiro produto (ID: {first_product_id}) ===\n'))
                self.debug_product_details(tiny_search, first_product_id)

        elif product_id:
            self.stdout.write(self.style.WARNING(f'\n=== Buscando detalhes do produto ID: {product_id} ===\n'))
            self.debug_product_details(tiny_search, product_id)

        else:
            self.stdout.write(self.style.ERROR('Use --search ou --id'))

    def debug_product_details(self, tiny_search, product_id):
        """Debug product details and variations"""

        # Get product details
        details = tiny_search.get_product_details(product_id)

        if not details:
            self.stdout.write(self.style.ERROR('Não foi possível obter detalhes do produto'))
            return

        self.stdout.write(self.style.SUCCESS('Detalhes do produto obtidos com sucesso!\n'))

        # Show basic info
        self.stdout.write(f'Nome: {details.get("nome", "N/A")}')
        self.stdout.write(f'Código: {details.get("codigo", "N/A")}')
        self.stdout.write(f'Tipo: {details.get("tipo", "N/A")}')
        self.stdout.write(f'Unidade: {details.get("unidade", "N/A")}')
        self.stdout.write(f'Preço: {details.get("preco", "N/A")}')
        self.stdout.write('')

        # Show variations
        variacoes = details.get('variacoes', [])

        if not variacoes:
            self.stdout.write(self.style.WARNING('⚠️  Este produto NÃO possui variações'))
            self.stdout.write(f'Saldo total: {details.get("saldo", 0)}')
            return

        self.stdout.write(self.style.SUCCESS(f'✓ Este produto possui {len(variacoes)} variações:\n'))

        total_stock = 0
        for i, variacao in enumerate(variacoes, 1):
            grade = variacao.get('grade', {})
            grade_nome = grade.get('nome', 'SEM NOME')
            saldo = variacao.get('saldo', 0)
            total_stock += float(saldo)

            self.stdout.write(f'{i}. Variação: {grade_nome}')
            self.stdout.write(f'   Saldo: {saldo}')

            # Show all fields in variation
            self.stdout.write('   Campos disponíveis:')
            for key, value in variacao.items():
                if key != 'grade':
                    self.stdout.write(f'     - {key}: {value}')
            self.stdout.write('')

        self.stdout.write(self.style.SUCCESS(f'Total em estoque (soma das variações): {total_stock}\n'))

        # Test size mapping
        self.stdout.write(self.style.WARNING('=== Testando Mapeamento de Tamanhos ===\n'))

        size_stock = tiny_search.map_size_variations(variacoes)

        self.stdout.write('Resultado do mapeamento:')
        self.stdout.write(f'  P:  {size_stock["P"]}')
        self.stdout.write(f'  M:  {size_stock["M"]}')
        self.stdout.write(f'  G:  {size_stock["G"]}')
        self.stdout.write(f'  GG: {size_stock["GG"]}')
        self.stdout.write(f'  Total: {sum(size_stock.values())}')
        self.stdout.write('')

        # Check if any size wasn't mapped
        mapped_total = sum(size_stock.values())
        if mapped_total < total_stock:
            self.stdout.write(self.style.WARNING(
                f'⚠️  ATENÇÃO: {total_stock - mapped_total} unidades NÃO foram mapeadas para nenhum tamanho!'
            ))
            self.stdout.write(self.style.WARNING(
                'Isso significa que os nomes das variações não correspondem aos padrões reconhecidos.'
            ))
            self.stdout.write('')
            self.stdout.write('Nomes das variações que não foram mapeados:')

            for variacao in variacoes:
                grade_nome = variacao.get('grade', {}).get('nome', '').upper().strip()
                matched = False

                size_mappings = {
                    'P': ['P', 'PP', 'PEQUENO', 'SMALL', 'S'],
                    'M': ['M', 'MEDIO', 'MÉDIO', 'MEDIUM'],
                    'G': ['G', 'GRANDE', 'LARGE', 'L'],
                    'GG': ['GG', 'XG', 'XL', 'EXTRA GRANDE', 'EXTRA LARGE', 'XXL']
                }

                for our_size, tiny_sizes in size_mappings.items():
                    for tiny_size in tiny_sizes:
                        if tiny_size in grade_nome:
                            matched = True
                            break
                    if matched:
                        break

                if not matched and variacao.get('saldo', 0) > 0:
                    self.stdout.write(f'  - "{grade_nome}" (saldo: {variacao.get("saldo", 0)})')

        elif mapped_total == total_stock:
            self.stdout.write(self.style.SUCCESS('✓ Todas as variações foram mapeadas corretamente!'))

        self.stdout.write('')

        # Show raw JSON
        self.stdout.write(self.style.WARNING('=== JSON Completo das Variações (para análise) ===\n'))
        self.stdout.write(json.dumps(variacoes, indent=2, ensure_ascii=False))
