from django.urls import path
from . import views

app_name = 'pedido'

urlpatterns = [
    path('', views.pedido_list, name='pedido_list'),
    
    # Client views
    path('checkout/', views.checkout_view, name='checkout'),
    path('<int:pedido_id>/status/', views.status_view, name='status'),
    path('historico/', views.historico_view, name='historico'),
    
    # ==================== API ENDPOINTS - CLIENTE ====================
    
    # Gestão de pedidos
    path('criar/', views.criar_pedido, name='api_criar_pedido'),
    path('<int:pedido_id>/finalizar/', views.finalizar_pedido, name='api_finalizar_pedido'),
    path('<int:pedido_id>/cancelar/', views.cancelar_pedido, name='api_cancelar_pedido'),
    path('<int:pedido_id>/', views.obter_pedido, name='api_obter_pedido'),
    path('meus-pedidos/', views.listar_pedidos_cliente, name='api_listar_pedidos_cliente'),
    
    # Gestão de itens
    path('item/adicionar/', views.adicionar_item, name='api_adicionar_item'),
    path('item/remover/', views.remover_item, name='api_remover_item'),
    path('item/atualizar-quantidade/', views.atualizar_quantidade_item, name='api_atualizar_quantidade_item'),
    
    # Pagamento
    path('processar-pagamento/', views.processar_pagamento, name='api_processar_pagamento'),
    
    # ==================== API ENDPOINTS - RESTAURANTE ====================
    
    # Gestão de status (prefixo _ para rotas do restaurante)
    path('_pedido/<int:pedido_id>/atualizar-status/', views._atualizar_status, name='api_restaurante_atualizar_status'),
    path('_pedido/<int:pedido_id>/avancar-status/', views._avancar_status, name='api_restaurante_avancar_status'),
    
    # Consultas detalhadas (prefixo _ para rotas do restaurante)
    path('_pedido/<int:pedido_id>/detalhes/', views._obter_detalhes_pedido, name='api_restaurante_obter_detalhes'),
    path('_pedido/<int:pedido_id>/estatisticas/', views._obter_estatisticas_pedido, name='api_restaurante_obter_estatisticas'),
    path('_pedidos/por-status/', views._listar_pedidos_por_status, name='api_restaurante_listar_por_status'),
]