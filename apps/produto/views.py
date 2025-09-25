# Views básicas para produtos - funcionalidades movidas para apps apropriados
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import logging

from .models import (
    Produto, Alimento, Bebida, Comida, Combo, RestricaoAlimentar, ComboItem
)

logger = logging.getLogger(__name__)

def produto_home(request):
    """
    Renderiza a página principal de produtos (cardápio) e envia os dados
    para serem consumidos pelo frontend (React).
    """
    produtos = Produto.objects.filter(available=True)

    produtos_data = []
    for produto in produtos:
        item = {
            'id': produto.id,
            'name': produto.name,
            'price': str(produto.price),
            'description': produto.description,
            'category': produto.category,
            'image_url': produto.image.url if produto.image else None,
        }
        produtos_data.append(item)

    context = {
        'produtos_data': produtos_data
    }

    logger.info(f"Enviando {len(produtos_data)} produtos para o template produto_home.html")
    return render(request, 'produto/produto_home.html', context)

def produto_list(request):
    """Lista todos os produtos disponíveis."""
    produtos = Produto.objects.filter(available=True)
    produtos_data = []
    for produto in produtos:
        produtos_data.append({
            'id': produto.id,
            'name': produto.name,
            'price': str(produto.price),
            'description': produto.description,
            'category': produto.category,
            'created_at': produto.created_at.isoformat(),
        })
    return JsonResponse({'produtos': produtos_data})

def produto_detail(produto_id):
    """Detalhes de um produto específico."""
    produto = get_object_or_404(Produto, id=produto_id)
    produto_data = {
        'id': produto.id,
        'name': produto.name,
        'price': str(produto.price),
        'description': produto.description,
        'category': produto.category,
        'available': produto.available,
    }
    return JsonResponse({'produto': produto_data})
