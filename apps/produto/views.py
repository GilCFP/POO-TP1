# Views básicas para produtos - funcionalidades movidas para apps apropriados
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from .models import (
    Produto, Alimento, Bebida, Comida, Combo, RestricaoAlimentar, ComboItem
)

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
            'preparation_time': produto.preparation_time,
            'calories': produto.calories,
        })
    return JsonResponse({'produtos': produtos_data})

def produto_detail(request, produto_id):
    """Detalhes de um produto específico."""
    produto = get_object_or_404(Produto, id=produto_id)
    produto_data = {
        'id': produto.id,
        'name': produto.name,
        'price': str(produto.price),
        'description': produto.description,
        'category': produto.category,
        'preparation_time': produto.preparation_time,
        'calories': produto.calories,
        'available': produto.available,
    }
    return JsonResponse({'produto': produto_data})
