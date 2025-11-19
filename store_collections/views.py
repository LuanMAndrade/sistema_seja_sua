from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Collection, Piece, Fabric, Accessory
from .forms import CollectionForm, PieceForm


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
def accessories_list(request):
    """List all accessories"""
    accessories = Accessory.objects.all()

    context = {
        'accessories': accessories,
        'total_accessories': accessories.count(),
    }
    return render(request, 'store_collections/accessories_list.html', context)


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
