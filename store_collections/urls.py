from django.urls import path
from . import views

app_name = 'store_collections'

urlpatterns = [
    path('collections/', views.collections_list, name='collections_list'),
    path('collections/new/', views.collection_create, name='collection_create'),
    path('collections/<int:pk>/', views.collection_detail, name='collection_detail'),
    path('collections/<int:pk>/edit/', views.collection_edit, name='collection_edit'),
    path('collections/<int:pk>/delete/', views.collection_delete, name='collection_delete'),
    path('pieces/', views.pieces_list, name='pieces_list'),
    path('pieces/new/', views.piece_create, name='piece_create'),
    path('pieces/<int:pk>/', views.piece_detail, name='piece_detail'),
    path('pieces/<int:pk>/edit/', views.piece_edit, name='piece_edit'),
    path('fabrics/', views.fabrics_list, name='fabrics_list'),
    # Inventory/Stock page
    path('inventory/', views.inventory_stock, name='inventory_stock'),
    # Accessories search
    path('api/accessories/search/', views.search_accessories, name='search_accessories'),
    # Tiny ERP integration
    path('api/tiny/search/', views.search_tiny_products, name='search_tiny_products'),
    path('api/tiny/link/', views.link_tiny_product, name='link_tiny_product'),
    path('api/sync-piece/<int:piece_id>/', views.sync_single_piece, name='sync_single_piece'),
    path('api/sync-all-pieces/', views.sync_all_pieces_endpoint, name='sync_all_pieces'),
]
