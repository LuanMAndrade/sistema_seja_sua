from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('collection-stock/', views.collection_pieces_stock, name='collection_stock'),
    path('pieces/', views.inventory_list, name='inventory_list'),
    path('accessories/', views.accessories_list, name='accessories_list'),
]
