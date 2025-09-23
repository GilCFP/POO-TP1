from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Pedido
from apps.cliente.services.cliente_service import ClienteService


# Placeholder views - implementar conforme necessário
def pedido_list(request):
    return JsonResponse({'message': 'Pedido list view'})


def checkout_view(request):
    """View para página de checkout."""
    # Verifica se cliente está autenticado
    if not getattr(request, 'is_client_authenticated', False):
        return render(request, 'client/login_required.html')
    
    client = request.client
    
    # Buscar pedido ativo do cliente
    pedido = Pedido.objects.filter(cliente=client, status='pendente').first()
    
    if not pedido:
        # Se não há pedido pendente, criar estrutura vazia
        checkout_data = {
            'pedido': None,
            'client': ClienteService.get_client_summary(client),
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
            },
            'client': ClienteService.get_client_summary(client)
        }
    
    return render(request, 'client/checkout.html', {
        'checkout_data': checkout_data
    })


def status_view(request, pedido_id):
    """View para página de status do pedido."""
    # Verifica se cliente está autenticado
    if not getattr(request, 'is_client_authenticated', False):
        return render(request, 'client/login_required.html')
    
    client = request.client
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=client)
    
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
        },
        'client': ClienteService.get_client_summary(client)
    }
    
    return render(request, 'client/status.html', {
        'status_data': status_data,
        'pedido': pedido
    })


def historico_view(request):
    """View para página de histórico de pedidos."""
    # Verifica se cliente está autenticado
    if not getattr(request, 'is_client_authenticated', False):
        return render(request, 'client/login_required.html')
    
    client = request.client
    
    # Buscar todos os pedidos do cliente
    pedidos = Pedido.objects.filter(cliente=client).order_by('-created_at')
    
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
        ],
        'client': ClienteService.get_client_summary(client)
    }
    
    return render(request, 'client/historico.html', {
        'historico_data': historico_data
    })
