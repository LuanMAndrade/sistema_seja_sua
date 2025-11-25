from django.urls import path
from . import views

app_name = 'sales_stats'

urlpatterns = [
    path('', views.statistics_dashboard, name='dashboard'),
    path('gerar-reposicao/', views.generate_replenishment, name='generate_replenishment'),
]
