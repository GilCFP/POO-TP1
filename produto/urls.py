from django.urls import path
from . import views

app_name = 'produto'

urlpatterns = [
    # URLs para Restaurante
    path('restaurantes/', views.listar_restaurantes, name='listar_restaurantes'),
    path('restaurantes/criar/', views.criar_restaurante, name='criar_restaurante'),
    
    # URLs para Cliente
    path('clientes/', views.listar_clientes, name='listar_clientes'),
    path('clientes/criar/', views.criar_cliente, name='criar_cliente'),
    path('clientes/<int:cliente_id>/adicionar-saldo/', views.adicionar_saldo_cliente, name='adicionar_saldo_cliente'),
    
    # URLs para Pedido
    path('pedidos/', views.listar_pedidos, name='listar_pedidos'),
    path('pedidos/criar/<int:cliente_id>/', views.criar_pedido, name='criar_pedido'),
    path('pedidos/<int:pedido_id>/editar/', views.editar_pedido, name='editar_pedido'),
    path('pedidos/<int:pedido_id>/finalizar/', views.finalizar_pedido, name='finalizar_pedido'),
    path('pedidos/<int:pedido_id>/pagamento/', views.processar_pagamento, name='processar_pagamento'),
    
    # URLs para Cozinha
    path('cozinha/', views.gerenciar_cozinha, name='gerenciar_cozinha'),
    
    # URLs para Produtos
    path('produtos/', views.listar_produtos, name='listar_produtos'),
    path('produtos/<int:produto_id>/desconto/', views.aplicar_desconto_produto, name='aplicar_desconto_produto'),
    
    # APIs
    path('api/verificar-restricoes/', views.api_verificar_restricoes, name='api_verificar_restricoes'),
    path('api/status-cozinha/', views.api_status_cozinha, name='api_status_cozinha'),
]