from django.urls import path
from . import views

app_name = 'pedido'

urlpatterns = [
    path('', views.pedido_list, name='pedido_list'),
    
    # Client views
    path('checkout/', views.checkout_view, name='checkout'),
    path('<int:pedido_id>/status/', views.status_view, name='status'),
    path('historico/', views.historico_view, name='historico'),
]