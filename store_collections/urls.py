from django.urls import path
from . import views

app_name = 'store_collections'

urlpatterns = [
    path('collections/', views.collections_list, name='collections_list'),
    path('collections/new/', views.collection_create, name='collection_create'),
    path('collections/<int:pk>/', views.collection_detail, name='collection_detail'),
    path('collections/<int:pk>/edit/', views.collection_edit, name='collection_edit'),
    path('pieces/', views.pieces_list, name='pieces_list'),
    path('pieces/new/', views.piece_create, name='piece_create'),
    path('pieces/<int:pk>/', views.piece_detail, name='piece_detail'),
    path('pieces/<int:pk>/edit/', views.piece_edit, name='piece_edit'),
    path('fabrics/', views.fabrics_list, name='fabrics_list'),
    path('accessories/', views.accessories_list, name='accessories_list'),
]
