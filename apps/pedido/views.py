from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Pedido

# Placeholder views - implementar conforme necessário
def pedido_list(request):
    return JsonResponse({'message': 'Pedido list view'})

@login_required
def checkout_view(request):
    # Buscar pedido ativo do usuário ou criar um novo
    pedido = Pedido.objects.filter(usuario=request.user, status='pendente').first()
    
    if not pedido:
        # Se não há pedido pendente, redirecionar ou criar um vazio
        checkout_data = {
            'pedido': None,
            'message': 'Nenhum pedido pendente encontrado'
        }
    else:
        checkout_data = {
            'pedido': {
                'id': pedido.id,
                'items': [
                    {
                        'produto': {'nome': item.produto.nome if hasattr(item, 'produto') else 'Produto'},
                        'quantity': getattr(item, 'quantity', 1),
                        'price': float(getattr(item, 'price', 0))
                    } for item in getattr(pedido, 'items', [])
                ],
                'total_price': float(getattr(pedido, 'total_price', 0)),
                'status': pedido.status
            }
        }
    
    return render(request, 'client/checkout.html', {
        'checkout_data': checkout_data
    })

@login_required
def status_view(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    status_data = {
        'pedido': {
            'id': pedido.id,
            'status': pedido.status,
            'created_at': pedido.created_at.isoformat() if hasattr(pedido, 'created_at') else None,
            'estimated_delivery': getattr(pedido, 'estimated_delivery', None),
            'items': [
                {
                    'produto': {'nome': item.produto.nome if hasattr(item, 'produto') else 'Produto'},
                    'quantity': getattr(item, 'quantity', 1),
                    'price': float(getattr(item, 'price', 0))
                } for item in getattr(pedido, 'items', [])
            ],
            'total_price': float(getattr(pedido, 'total_price', 0)),
            'delivery_address': getattr(pedido, 'delivery_address', None)
        }
    }
    
    return render(request, 'client/status.html', {
        'status_data': status_data,
        'pedido': pedido
    })

@login_required
def historico_view(request):
    # Buscar todos os pedidos do usuário
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-created_at')
    
    historico_data = {
        'pedidos': [
            {
                'id': pedido.id,
                'status': pedido.status,
                'created_at': pedido.created_at.isoformat() if hasattr(pedido, 'created_at') else None,
                'items': [
                    {
                        'produto': {'nome': item.produto.nome if hasattr(item, 'produto') else 'Produto'},
                        'quantity': getattr(item, 'quantity', 1),
                        'price': float(getattr(item, 'price', 0))
                    } for item in getattr(pedido, 'items', [])
                ],
                'total_price': float(getattr(pedido, 'total_price', 0))
            } for pedido in pedidos[:20]  # Limitar a 20 pedidos iniciais
        ]
    }
    
    return render(request, 'client/historico.html', {
        'historico_data': historico_data
    })