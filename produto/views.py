from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models import (
    Produto, Cliente, Pedido, Restaurante, Cozinha, Caixa,
    StatusPedido, Alimento, Bebida, Comida
)
from .services.business_services import (
    RestauranteService, ClienteService, PedidoService,
    PagamentoService, CozinhaService, ProdutoService
)


# Views para Restaurante
def criar_restaurante(request):
    """View para criar um novo restaurante."""
    if request.method == 'POST':
        try:
            nome = request.POST.get('nome')
            numero_chefs = int(request.POST.get('numero_chefs', 1))
            caixa_inicial = float(request.POST.get('caixa_inicial', 0.0))
            
            restaurante = RestauranteService.criar_restaurante(
                nome=nome,
                numero_chefs=numero_chefs,
                caixa_inicial=caixa_inicial
            )
            
            messages.success(request, f'Restaurante "{restaurante.name}" criado com sucesso!')
            return redirect('listar_restaurantes')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar restaurante: {str(e)}')
    
    return render(request, 'produto/criar_restaurante.html')


def listar_restaurantes(request):
    """View para listar restaurantes."""
    restaurantes = Restaurante.objects.all()
    return render(request, 'produto/listar_restaurantes.html', {
        'restaurantes': restaurantes
    })


# Views para Cliente
def criar_cliente(request):
    """View para criar um novo cliente."""
    if request.method == 'POST':
        try:
            nome = request.POST.get('nome')
            endereco = request.POST.get('endereco', '')
            saldo_inicial = float(request.POST.get('saldo_inicial', 0.0))
            
            cliente = ClienteService.criar_cliente(
                nome=nome,
                endereco=endereco,
                saldo_inicial=saldo_inicial
            )
            
            messages.success(request, f'Cliente "{cliente.name}" criado com sucesso!')
            return redirect('listar_clientes')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar cliente: {str(e)}')
    
    return render(request, 'produto/criar_cliente.html')


def listar_clientes(request):
    """View para listar clientes."""
    clientes = Cliente.objects.all()
    return render(request, 'produto/listar_clientes.html', {
        'clientes': clientes
    })


def adicionar_saldo_cliente(request, cliente_id):
    """View para adicionar saldo a um cliente."""
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    if request.method == 'POST':
        try:
            valor = float(request.POST.get('valor'))
            ClienteService.adicionar_saldo(cliente_id, valor)
            
            messages.success(request, f'Saldo adicionado com sucesso! Novo saldo: R$ {cliente.balance:.2f}')
            return redirect('listar_clientes')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar saldo: {str(e)}')
    
    return render(request, 'produto/adicionar_saldo.html', {'cliente': cliente})


# Views para Pedido
def criar_pedido(request, cliente_id):
    """View para criar um novo pedido."""
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    try:
        pedido = PedidoService.criar_pedido(cliente_id)
        messages.success(request, 'Pedido criado com sucesso!')
        return redirect('editar_pedido', pedido_id=pedido.id)
        
    except Exception as e:
        messages.error(request, f'Erro ao criar pedido: {str(e)}')
        return redirect('listar_clientes')


def editar_pedido(request, pedido_id):
    """View para editar um pedido (adicionar/remover itens)."""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    produtos_disponiveis = Produto.objects.filter(available=True)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        produto_id = request.POST.get('produto_id')
        quantidade = int(request.POST.get('quantidade', 1))
        
        try:
            if action == 'adicionar':
                PedidoService.adicionar_item_ao_pedido(pedido_id, produto_id, quantidade)
                messages.success(request, 'Item adicionado ao pedido!')
                
            elif action == 'remover':
                PedidoService.remover_item_do_pedido(pedido_id, produto_id)
                messages.success(request, 'Item removido do pedido!')
                
        except Exception as e:
            messages.error(request, f'Erro: {str(e)}')
        
        return redirect('editar_pedido', pedido_id=pedido_id)
    
    return render(request, 'produto/editar_pedido.html', {
        'pedido': pedido,
        'produtos_disponiveis': produtos_disponiveis,
        'itens_pedido': pedido.itempedido_set.all()
    })


def finalizar_pedido(request, pedido_id):
    """View para finalizar um pedido."""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    try:
        PedidoService.finalizar_pedido(pedido_id)
        messages.success(request, 'Pedido finalizado! Pronto para pagamento.')
        return redirect('processar_pagamento', pedido_id=pedido_id)
        
    except Exception as e:
        messages.error(request, f'Erro ao finalizar pedido: {str(e)}')
        return redirect('editar_pedido', pedido_id=pedido_id)


# Views para Pagamento
def processar_pagamento(request, pedido_id):
    """View para processar pagamento de um pedido."""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        try:
            # Assumindo que há apenas um caixa por enquanto
            caixa = Caixa.objects.first()
            if not caixa:
                raise ValidationError("Nenhum caixa disponível")
            
            PagamentoService.processar_pagamento(pedido_id, caixa.id)
            messages.success(request, 'Pagamento processado com sucesso!')
            
            # Adicionar à fila da cozinha
            cozinha = Cozinha.objects.first()
            if cozinha:
                CozinhaService.adicionar_pedido_na_fila(cozinha.id, pedido_id)
                messages.success(request, 'Pedido adicionado à fila da cozinha!')
            
            return redirect('listar_pedidos')
            
        except Exception as e:
            messages.error(request, f'Erro no pagamento: {str(e)}')
    
    return render(request, 'produto/processar_pagamento.html', {'pedido': pedido})


def listar_pedidos(request):
    """View para listar todos os pedidos."""
    pedidos = Pedido.objects.all().order_by('-created_at')
    return render(request, 'produto/listar_pedidos.html', {'pedidos': pedidos})


# Views para Cozinha
def gerenciar_cozinha(request):
    """View para gerenciar a cozinha."""
    cozinha = Cozinha.objects.first()
    if not cozinha:
        messages.error(request, 'Nenhuma cozinha configurada')
        return redirect('admin:index')
    
    pedidos_em_fila = cozinha.orders_in_queue.all()
    pedidos_em_progresso = cozinha.orders_in_progress.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        try:
            if action == 'iniciar_proximo':
                CozinhaService.iniciar_proximo_pedido(cozinha.id)
                messages.success(request, 'Próximo pedido iniciado!')
                
            elif action == 'finalizar_pedido':
                pedido_id = request.POST.get('pedido_id')
                CozinhaService.finalizar_pedido(cozinha.id, pedido_id)
                messages.success(request, 'Pedido finalizado!')
                
        except Exception as e:
            messages.error(request, f'Erro: {str(e)}')
        
        return redirect('gerenciar_cozinha')
    
    return render(request, 'produto/gerenciar_cozinha.html', {
        'cozinha': cozinha,
        'pedidos_em_fila': pedidos_em_fila,
        'pedidos_em_progresso': pedidos_em_progresso
    })


# Views para Produtos
def listar_produtos(request):
    """View para listar produtos."""
    produtos = Produto.objects.all()
    produtos_vencidos = ProdutoService.verificar_produtos_vencidos()
    
    return render(request, 'produto/listar_produtos.html', {
        'produtos': produtos,
        'produtos_vencidos': produtos_vencidos
    })


def aplicar_desconto_produto(request, produto_id):
    """View para aplicar desconto a um produto."""
    produto = get_object_or_404(Produto, id=produto_id)
    
    if request.method == 'POST':
        try:
            desconto = float(request.POST.get('desconto'))
            ProdutoService.aplicar_desconto(produto_id, desconto)
            messages.success(request, f'Desconto aplicado ao produto "{produto.name}"!')
            
        except Exception as e:
            messages.error(request, f'Erro ao aplicar desconto: {str(e)}')
        
        return redirect('listar_produtos')
    
    return render(request, 'produto/aplicar_desconto.html', {'produto': produto})


# API Views (para uso com JavaScript/AJAX)
@csrf_exempt
def api_verificar_restricoes(request):
    """API para verificar restrições alimentares de um cliente para um produto."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cliente_id = data.get('cliente_id')
            produto_id = data.get('produto_id')
            
            pode_consumir = ClienteService.verificar_restricoes_produto(cliente_id, produto_id)
            
            return JsonResponse({
                'pode_consumir': pode_consumir,
                'status': 'success'
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'status': 'error'
            }, status=400)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@csrf_exempt 
def api_status_cozinha(request):
    """API para obter status da cozinha."""
    try:
        cozinha = Cozinha.objects.first()
        if not cozinha:
            return JsonResponse({'error': 'Cozinha não encontrada'}, status=404)
        
        return JsonResponse({
            'capacidade_atual': cozinha.current_capacity,
            'capacidade_maxima': cozinha.full_capacity,
            'pedidos_em_fila': cozinha.orders_in_queue.count(),
            'pedidos_em_progresso': cozinha.orders_in_progress.count(),
            'status': 'success'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
