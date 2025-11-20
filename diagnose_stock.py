#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to diagnose stock status
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store_management.settings')
django.setup()

from store_collections.models import Piece
from inventory.models import InventoryPiece

print('='*60)
print('DIAGNOSTICO DE ESTOQUE')
print('='*60)

print('\n=== Pecas Cadastradas no Aplicativo ===')
pieces = Piece.objects.all()
print(f'Total de pecas: {pieces.count()}')

for p in pieces[:10]:
    print(f'\nPeca ID {p.id}:')
    print(f'  - Colecao: {p.collection.name}')
    print(f'  - Categoria: {p.category}')
    print(f'  - Estoque Atual: P={p.current_stock_p}, M={p.current_stock_m}, G={p.current_stock_g}, GG={p.current_stock_gg}')
    print(f'  - Total Estoque: {p.total_current_stock}')
    print(f'  - Vinculado ao Tiny: {p.is_synced_with_tiny}')
    if p.tiny_erp_piece:
        print(f'  - Tiny ERP Piece: {p.tiny_erp_piece.name} (ID: {p.tiny_erp_piece.id})')

print('\n' + '='*60)
print('=== Inventory Pieces (Tiny ERP) ===')
inv_pieces = InventoryPiece.objects.all()
print(f'Total no inventario: {inv_pieces.count()}')

for ip in inv_pieces[:10]:
    print(f'\nInventory Piece ID {ip.id}:')
    print(f'  - Nome: {ip.name}')
    print(f'  - External ID: {ip.external_id}')
    print(f'  - Quantidade Total: {ip.quantity}')
    print(f'  - Tem Variacoes: {ip.has_variations}')
    print(f'  - Estoque por tamanho: P={ip.stock_p}, M={ip.stock_m}, G={ip.stock_g}, GG={ip.stock_gg}')
    linked_count = ip.linked_pieces.count()
    print(f'  - Pecas vinculadas: {linked_count}')

print('\n' + '='*60)
print('RESUMO')
print('='*60)
print(f'Pecas cadastradas: {pieces.count()}')
print(f'Pecas vinculadas ao Tiny: {pieces.filter(tiny_erp_piece__isnull=False).count()}')
print(f'Produtos no Tiny ERP: {inv_pieces.count()}')
print(f'Pecas com estoque > 0: {pieces.filter(current_stock_p__gt=0).count() + pieces.filter(current_stock_m__gt=0).count() + pieces.filter(current_stock_g__gt=0).count() + pieces.filter(current_stock_gg__gt=0).count()}')
