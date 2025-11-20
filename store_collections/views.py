from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Collection, Piece, Fabric
from .forms import CollectionForm, PieceForm
from .tiny_search import TinyERPSearch
from inventory.models import InventoryAccessory


@login_required
def collections_list(request):
    """List all collections"""
    collections = Collection.objects.all().order_by('-created_at')

    context = {
        'collections': collections,
        'total_collections': collections.count(),
    }
    return render(request, 'store_collections/collections_list.html', context)


@login_required
def collection_detail(request, pk):
    """View details of a specific collection"""
    collection = get_object_or_404(Collection, pk=pk)
    pieces = collection.pieces.all()

    context = {
        'collection': collection,
        'pieces': pieces,
        'total_pieces': pieces.count(),
    }
    return render(request, 'store_collections/collection_detail.html', context)


@login_required
def pieces_list(request):
    """List all pieces"""
    pieces = Piece.objects.select_related('collection', 'fabric', 'category').all()

    context = {
        'pieces': pieces,
        'total_pieces': pieces.count(),
    }
    return render(request, 'store_collections/pieces_list.html', context)


@login_required
def piece_detail(request, pk):
    """View details of a specific piece"""
    piece = get_object_or_404(Piece.objects.select_related('collection', 'fabric', 'category'), pk=pk)
    colors = piece.colors.all()
    images = piece.images.all()

    context = {
        'piece': piece,
        'colors': colors,
        'images': images,
    }
    return render(request, 'store_collections/piece_detail.html', context)


@login_required
def fabrics_list(request):
    """List all fabrics"""
    fabrics = Fabric.objects.select_related('supplier').all()

    context = {
        'fabrics': fabrics,
        'total_fabrics': fabrics.count(),
    }
    return render(request, 'store_collections/fabrics_list.html', context)


@login_required
def collection_create(request):
    """Criar nova coleção"""
    if request.method == 'POST':
        form = CollectionForm(request.POST)
        if form.is_valid():
            collection = form.save()
            messages.success(request, f'Coleção "{collection.name}" criada com sucesso!')
            return redirect('store_collections:collection_detail', pk=collection.pk)
    else:
        form = CollectionForm()

    context = {
        'form': form,
        'title': 'Nova Coleção',
        'action': 'Criar',
    }
    return render(request, 'store_collections/collection_form.html', context)


@login_required
def collection_edit(request, pk):
    """Editar coleção existente"""
    collection = get_object_or_404(Collection, pk=pk)

    if request.method == 'POST':
        form = CollectionForm(request.POST, instance=collection)
        if form.is_valid():
            collection = form.save()
            messages.success(request, f'Coleção "{collection.name}" atualizada com sucesso!')
            return redirect('store_collections:collection_detail', pk=collection.pk)
    else:
        form = CollectionForm(instance=collection)

    context = {
        'form': form,
        'title': f'Editar Coleção: {collection.name}',
        'action': 'Salvar',
        'collection': collection,
    }
    return render(request, 'store_collections/collection_form.html', context)


@login_required
def piece_create(request):
    """Criar nova peça"""
    if request.method == 'POST':
        form = PieceForm(request.POST)
        if form.is_valid():
            piece = form.save()
            messages.success(request, 'Peça criada com sucesso!')
            return redirect('store_collections:piece_detail', pk=piece.pk)
    else:
        form = PieceForm()

    context = {
        'form': form,
        'title': 'Nova Peça',
        'action': 'Criar',
    }
    return render(request, 'store_collections/piece_form.html', context)


@login_required
def piece_edit(request, pk):
    """Editar peça existente"""
    piece = get_object_or_404(Piece, pk=pk)

    if request.method == 'POST':
        form = PieceForm(request.POST, instance=piece)
        if form.is_valid():
            piece = form.save()
            messages.success(request, 'Peça atualizada com sucesso!')
            return redirect('store_collections:piece_detail', pk=piece.pk)
    else:
        form = PieceForm(instance=piece)

    context = {
        'form': form,
        'title': f'Editar Peça',
        'action': 'Salvar',
        'piece': piece,
    }
    return render(request, 'store_collections/piece_form.html', context)


@login_required
def collection_delete(request, pk):
    """Excluir coleção e seus eventos relacionados"""
    collection = get_object_or_404(Collection, pk=pk)

    if request.method == 'POST':
        collection_name = collection.name
        events_count = collection.events.count()
        pieces_count = collection.pieces.count()

        # A exclusão em cascata irá excluir automaticamente:
        # - CalendarEvents relacionados (on_delete=CASCADE)
        # - Pieces relacionados (on_delete=CASCADE)
        # - PieceColors relacionados (via Piece CASCADE)
        # - PieceImages relacionados (via Piece CASCADE)
        collection.delete()

        messages.success(
            request,
            f'Coleção "{collection_name}" excluída com sucesso! '
            f'{pieces_count} peça(s) e {events_count} evento(s) também foram removidos.'
        )
        return redirect('store_collections:collections_list')

    # GET request - mostrar página de confirmação
    context = {
        'collection': collection,
        'events_count': collection.events.count(),
        'pieces_count': collection.pieces.count(),
    }
    return render(request, 'store_collections/collection_confirm_delete.html', context)


@login_required
@require_http_methods(["GET"])
def search_accessories(request):
    """
    AJAX endpoint to search inventory accessories by name
    """
    search_term = request.GET.get('q', '').strip()

    if not search_term:
        return JsonResponse({
            'success': False,
            'error': 'Informe um termo de busca'
        }, status=400)

    # Search inventory accessories by name (case-insensitive)
    accessories = InventoryAccessory.objects.filter(
        name__icontains=search_term
    ).order_by('name')[:20]  # Limit to 20 results

    results = [
        {
            'id': acc.id,
            'name': acc.name,
            'minimum_quantity': acc.minimum_quantity,
            'price': float(acc.price)
        }
        for acc in accessories
    ]

    return JsonResponse({
        'success': True,
        'accessories': results,
        'count': len(results)
    })


@login_required
@require_http_methods(["GET"])
def search_tiny_products(request):
    """
    AJAX endpoint to search products in Tiny ERP
    """
    search_term = request.GET.get('q', '').strip()

    if not search_term:
        return JsonResponse({
            'success': False,
            'error': 'Informe um termo de busca'
        }, status=400)

    if len(search_term) < 2:
        return JsonResponse({
            'success': False,
            'error': 'Digite pelo menos 2 caracteres para buscar'
        }, status=400)

    try:
        tiny_search = TinyERPSearch()
        products = tiny_search.search_products(search_term)

        return JsonResponse({
            'success': True,
            'products': products,
            'count': len(products)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao buscar produtos: {str(e)}'
        }, status=500)


@login_required
def inventory_stock(request):
    """
    Página de estoque mostrando as peças cadastradas no aplicativo
    """
    pieces = Piece.objects.select_related(
        'collection', 'category', 'fabric', 'tiny_erp_piece'
    ).all().order_by('collection__name')

    synced_pieces = pieces.filter(tiny_erp_piece__isnull=False).count()
    total_stock = sum(piece.total_current_stock for piece in pieces)

    context = {
        'pieces': pieces,
        'total_pieces': pieces.count(),
        'synced_pieces': synced_pieces,
        'total_stock': total_stock,
    }
    return render(request, 'store_collections/inventory_stock.html', context)


@login_required
@require_http_methods(["POST"])
def sync_single_piece(request, piece_id):
    """
    AJAX endpoint to sync stock for a single piece
    """
    try:
        piece = get_object_or_404(Piece, pk=piece_id)

        if not piece.tiny_erp_piece:
            return JsonResponse({
                'success': False,
                'error': 'Peça não está vinculada ao Tiny ERP'
            }, status=400)

        from .tiny_erp_sync import TinyERPStockSync
        sync_service = TinyERPStockSync()

        success = sync_service.sync_piece_stock(piece)

        if success:
            return JsonResponse({
                'success': True,
                'message': f'Estoque sincronizado: P={piece.current_stock_p}, M={piece.current_stock_m}, G={piece.current_stock_g}, GG={piece.current_stock_gg}',
                'stock': {
                    'p': piece.current_stock_p,
                    'm': piece.current_stock_m,
                    'g': piece.current_stock_g,
                    'gg': piece.current_stock_gg,
                    'total': piece.total_current_stock
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Falha ao sincronizar estoque'
            }, status=500)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def sync_all_pieces_endpoint(request):
    """
    AJAX endpoint to sync stock for all linked pieces
    """
    try:
        from .tiny_erp_sync import TinyERPStockSync
        sync_service = TinyERPStockSync()

        success_count, error_count = sync_service.sync_all_pieces()

        return JsonResponse({
            'success': True,
            'synced': success_count,
            'errors': error_count,
            'message': f'{success_count} peça(s) sincronizada(s), {error_count} erro(s)'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def link_tiny_product(request):
    """
    AJAX endpoint to link a Tiny ERP product to a piece
    Creates/updates InventoryPiece and returns its ID
    """
    import json

    try:
        data = json.loads(request.body)
        product_data = data.get('product')

        if not product_data:
            return JsonResponse({
                'success': False,
                'error': 'Dados do produto não fornecidos'
            }, status=400)

        tiny_search = TinyERPSearch()
        inventory_piece = tiny_search.get_or_create_inventory_piece(product_data)

        if inventory_piece:
            return JsonResponse({
                'success': True,
                'inventory_piece_id': inventory_piece.id,
                'inventory_piece_name': inventory_piece.name,
                'message': 'Produto vinculado com sucesso!'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Erro ao criar/atualizar produto no inventário'
            }, status=500)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Dados JSON inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao vincular produto: {str(e)}'
        }, status=500)


@login_required
def tiny_debug(request):
    """
    Página de debug para visualizar JSONs retornados pela API Tiny ERP
    """
    import json as json_lib
    import requests

    search_term = request.GET.get('search', '').strip()
    product_id = request.GET.get('product_id', '').strip()

    context = {
        'search_term': search_term,
        'product_id': product_id,
        'search_results': None,
        'product_details': None,
        'variations_stock': None,
        'products_list': None,
    }

    if search_term:
        # Realizar busca
        tiny_search = TinyERPSearch()

        # JSON da busca de produtos
        endpoint = f"{tiny_search.api_url}/produtos.pesquisa.php"
        params = {
            'token': tiny_search.api_token,
            'formato': 'json',
            'pesquisa': search_term
        }

        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response_json = response.json()
            context['search_results'] = json_lib.dumps(response_json, indent=2, ensure_ascii=False)

            # Extrair lista de produtos para links clicáveis
            produtos = response_json.get('retorno', {}).get('produtos', [])
            if produtos:
                context['products_list'] = [
                    {
                        'id': item.get('produto', {}).get('id'),
                        'nome': item.get('produto', {}).get('nome'),
                    }
                    for item in produtos
                ]
        except Exception as e:
            context['search_error'] = str(e)

    if product_id:
        # Obter detalhes do produto
        tiny_search = TinyERPSearch()

        # JSON do produto.obter.php
        endpoint = f"{tiny_search.api_url}/produto.obter.php"
        params = {
            'token': tiny_search.api_token,
            'formato': 'json',
            'id': product_id
        }

        try:
            response = requests.get(endpoint, params=params, timeout=10)
            product_json = response.json()
            context['product_details'] = json_lib.dumps(product_json, indent=2, ensure_ascii=False)

            # Se tiver variações, buscar estoque de cada uma
            produto = product_json.get('retorno', {}).get('produto', {})
            variacoes = produto.get('variacoes', [])

            if variacoes:
                variations_stock = []
                for variacao in variacoes:
                    var_id = variacao.get('id')
                    grade = variacao.get('grade', {})

                    if var_id:
                        # Buscar estoque da variação
                        stock_endpoint = f"{tiny_search.api_url}/produto.obter.estoque.php"
                        stock_params = {
                            'token': tiny_search.api_token,
                            'formato': 'json',
                            'id': var_id
                        }

                        try:
                            stock_response = requests.get(stock_endpoint, params=stock_params, timeout=10)
                            stock_json = stock_response.json()

                            variations_stock.append({
                                'variation_id': var_id,
                                'variation_name': grade.get('nome', 'N/A'),
                                'stock_json': json_lib.dumps(stock_json, indent=2, ensure_ascii=False),
                            })
                        except Exception as e:
                            variations_stock.append({
                                'variation_id': var_id,
                                'variation_name': grade.get('nome', 'N/A'),
                                'error': str(e),
                            })

                context['variations_stock'] = variations_stock

        except Exception as e:
            context['product_error'] = str(e)

    return render(request, 'store_collections/tiny_debug.html', context)
