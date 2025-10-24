from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Pedido, StatusPedido
from apps.cliente.models import Cliente
from apps.cliente.services.cliente_service import ClienteService
from .services.pedido_service import PedidoService
import json

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
    print(f"Buscando pedido para cliente ID: {client.id}")
    pedido = Pedido.objects.filter(cliente=client, status=StatusPedido.ORDERING).first()
    
    if not pedido:
        # Se não há pedido pendente, criar estrutura vazia
        print("Nenhum pedido pendente encontrado para o cliente.")
        checkout_data = {
            'pedido': None,
            'client': ClienteService.get_client_summary(client),
            'endereco_selecionado': {
                'street': '',
                'neighborhood': '',
                'complement': '',
                'reference': ''
            },
            'pagamento': {
                'method': 'card',
                'changeFor': ''
            },
            'message': 'Nenhum pedido pendente encontrado'
        }
    else:
        # Criar estrutura com dados dos items com IDs únicos
        pedido_items = []
        for i, item in enumerate(pedido.items.all()):
            pedido_items.append({
                'id': getattr(item, 'id', i + 1),  # Usar ID do item ou índice como fallback
                'produto': {
                    'nome': item.produto.nome if hasattr(item, 'produto') else 'Produto',
                    'descricao': getattr(item.produto, 'descricao', '') if hasattr(item, 'produto') else ''
                },
                'quantidade': getattr(item, 'quantidade', 1),
                'price': float(getattr(item, 'price', 0)),
                'subtotal': float(getattr(item, 'subtotal', getattr(item, 'price', 0) * getattr(item, 'quantidade', 1)))
            })
        
        checkout_data = {
            'pedido': {
                'id': pedido.id,
                'items': pedido_items,
                'total_price': float(getattr(pedido, 'total_price', 0)),
                'status': pedido.status
            },
            'client': ClienteService.get_client_summary(client),
            'endereco_selecionado': {
                'street': getattr(client, 'endereco', ''),
                'neighborhood': '',
                'complement': '',
                'reference': ''
            },
            'pagamento': {
                'method': 'card',
                'changeFor': ''
            }
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
                } for item in pedido.items.all()
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
                    } for item in pedido.items.all()
                ],
                'total_price': float(getattr(pedido, 'total_price', 0))
            } for pedido in pedidos[:20]  # Limitar a 20 pedidos iniciais
        ],
        'client': ClienteService.get_client_summary(client)
    }
    
    return render(request, 'client/historico.html', {
        'historico_data': historico_data
    })



# -------------------------------- API endpoints --------------------------------
@require_http_methods(["POST"])
def criar_pedido(request):
    """View para criar um novo pedido."""
    import logging
    logger = logging.getLogger(__name__)
    
    # Debug: log da requisição
    logger.info(f"Criando pedido - Headers: {dict(request.headers)}")
    logger.info(f"Criando pedido - Content-Type: {request.content_type}")
    logger.info(f"Criando pedido - CSRF Token: {request.META.get('HTTP_X_CSRFTOKEN', 'Não encontrado')}")
    logger.info(f"Criando pedido - Cliente autenticado: {getattr(request, 'is_client_authenticated', False)}")
    
    try:
        # Parse do JSON body
        data = json.loads(request.body)
        logger.info(f"Dados recebidos: {data}")
        
        # Verificar se cliente está autenticado
        if not getattr(request, 'is_client_authenticated', False):
            # Alternativa: obter client_id do body do request
            client_id = data.get('client_id')
            
            if not client_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Cliente não autenticado ou client_id não fornecido'
                }, status=401)
            
            # Buscar cliente pelo ID
            try:
                client = Cliente.objects.get(id=client_id, is_active=True)
                logger.info(f"Cliente encontrado via ID: {client.id}")
            except Cliente.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Cliente não encontrado'
                }, status=404)
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Erro ao buscar cliente: {str(e)}'
                }, status=400)
        else:
            client = request.client
            logger.info(f"Cliente autenticado via middleware: {client.id}")
        
        pedido = PedidoService.criar_pedido(
            cliente_id=client.id,
            delivery_address=data.get('delivery_address'),
            notes=data.get('notes'),
            usuario='Sistema'
        )

        return JsonResponse({
            'success': True,
            'message': 'Pedido criado com sucesso',
            'pedido_id': pedido.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Formato de JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao criar pedido: {str(e)}'
        }, status=500)

@require_http_methods(["POST"])
def cancelar_pedido(request, pedido_id):
    """View para cancelar um pedido."""
    try:
        # Verificar se cliente está autenticado
        if not getattr(request, 'is_client_authenticated', False):
            return JsonResponse({
                'success': False,
                'error': 'Cliente não autenticado'
            }, status=401)
        
        client = request.client
        
        # Verificar se o pedido pertence ao cliente
        pedido = get_object_or_404(Pedido, id=pedido_id, cliente=client)
        
        # Obter motivo do cancelamento
        data = json.loads(request.body) if request.body else {}
        motivo = data.get('motivo', 'Cancelado pelo cliente')
        
        # Cancelar pedido usando o service
        pedido_cancelado = PedidoService.cancelar_pedido(
            pedido_id=pedido_id,
            motivo=motivo,
            usuario=f'Cliente: {client.name}'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Pedido cancelado com sucesso',
            'pedido': {
                'id': pedido_cancelado.id,
                'status': pedido_cancelado.get_status_display()
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Formato de JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao cancelar pedido: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def adicionar_item(request):
    """View para adicionar item ao pedido."""
    try:
        # Verificar se cliente está autenticado
        if not getattr(request, 'is_client_authenticated', False):
            return JsonResponse({
                'success': False,
                'error': 'Cliente não autenticado'
            }, status=401)
        
        client = request.client
        data = json.loads(request.body)
        
        # Validar dados obrigatórios
        pedido_id = data.get('pedido_id')
        produto_id = data.get('produto_id')
        quantidade = data.get('quantidade', 1)
        instrucoes_especiais = data.get('instrucoes_especiais', '')
        
        if not pedido_id or not produto_id:
            return JsonResponse({
                'success': False,
                'error': 'pedido_id e produto_id são obrigatórios'
            }, status=400)
        
        # Verificar se o pedido pertence ao cliente
        pedido = get_object_or_404(Pedido, id=pedido_id, cliente=client)
        
        # Adicionar item usando o service
        item = PedidoService.adicionar_item(
            pedido_id=pedido_id,
            produto_id=produto_id,
            quantidade=quantidade,
            instrucoes_especiais=instrucoes_especiais
        )
        
        # Obter pedido atualizado
        pedido.refresh_from_db()
        
        return JsonResponse({
            'success': True,
            'message': 'Item adicionado com sucesso',
            'item': {
                'id': item.id,
                'produto': item.produto.name,
                'quantidade': item.quantidade,
                'subtotal': float(item.subtotal)
            },
            'pedido_total': float(pedido.total_price)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Formato de JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao adicionar item: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def remover_item(request):
    """View para remover item do pedido."""
    try:
        # Verificar se cliente está autenticado
        if not getattr(request, 'is_client_authenticated', False):
            return JsonResponse({
                'success': False,
                'error': 'Cliente não autenticado'
            }, status=401)
        
        client = request.client
        data = json.loads(request.body)
        
        # Validar dados obrigatórios
        pedido_id = data.get('pedido_id')
        produto_id = data.get('produto_id')
        
        if not pedido_id or not produto_id:
            return JsonResponse({
                'success': False,
                'error': 'pedido_id e produto_id são obrigatórios'
            }, status=400)
        
        # Verificar se o pedido pertence ao cliente
        pedido = get_object_or_404(Pedido, id=pedido_id, cliente=client)
        
        # Remover item usando o service
        PedidoService.remover_item(
            pedido_id=pedido_id,
            produto_id=produto_id
        )
        
        # Obter pedido atualizado
        pedido.refresh_from_db()
        
        return JsonResponse({
            'success': True,
            'message': 'Item removido com sucesso',
            'pedido_total': float(pedido.total_price)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Formato de JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao remover item: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def processar_pagamento(request):
    """View para processar pagamento do pedido."""
    try:
        # Verificar se cliente está autenticado
        if not getattr(request, 'is_client_authenticated', False):
            return JsonResponse({
                'success': False,
                'error': 'Cliente não autenticado'
            }, status=401)
        
        client = request.client
        data = json.loads(request.body)
        
        # Validar dados obrigatórios
        pedido_id = data.get('pedido_id')
        metodo_pagamento = data.get('metodo_pagamento')
        
        if not pedido_id:
            return JsonResponse({
                'success': False,
                'error': 'pedido_id é obrigatório'
            }, status=400)
        
        # Verificar se o pedido pertence ao cliente
        pedido = get_object_or_404(Pedido, id=pedido_id, cliente=client)
        
        # Processar pagamento usando o service
        pedido_pago = PedidoService.processar_pagamento(
            pedido_id=pedido_id,
            metodo_pagamento=metodo_pagamento,
            usuario=f'Cliente: {client.name}'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Pagamento processado com sucesso',
            'pedido': {
                'id': pedido_pago.id,
                'status': pedido_pago.get_status_display(),
                'metodo_pagamento': pedido_pago.payment_method
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Formato de JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao processar pagamento: {str(e)}'
        }, status=500)


# ==================== ROTAS DO RESTAURANTE (com prefixo _) ====================

@require_http_methods(["POST"])
def _atualizar_status(request, pedido_id):
    """View para restaurante atualizar status do pedido."""
    try:
        # Verificar se é usuário do restaurante (implementar autenticação específica)
        # Por enquanto, assumindo que há alguma verificação de permissão
        
        data = json.loads(request.body)
        novo_status = data.get('status')
        observacoes = data.get('observacoes', '')
        usuario = data.get('usuario', 'Sistema')
        
        if not novo_status:
            return JsonResponse({
                'success': False,
                'error': 'Novo status é obrigatório'
            }, status=400)
        
        # Validar se o status é válido
        status_validos = [choice[0] for choice in StatusPedido.choices]
        if novo_status not in status_validos:
            return JsonResponse({
                'success': False,
                'error': f'Status inválido. Opções: {status_validos}'
            }, status=400)
        
        # Atualizar status usando o service
        pedido = PedidoService.mudar_status(
            pedido_id=pedido_id,
            novo_status=novo_status,
            usuario=f'Restaurante: {usuario}',
            observacoes=observacoes
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Status atualizado com sucesso',
            'pedido': {
                'id': pedido.id,
                'status': pedido.get_status_display(),
                'status_code': pedido.status
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Formato de JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao atualizar status: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def _avancar_status(request, pedido_id):
    """View para restaurante avançar status do pedido automaticamente."""
    try:
        # Verificar se é usuário do restaurante
        data = json.loads(request.body) if request.body else {}
        usuario = data.get('usuario', 'Sistema')
        
        # Avançar status usando o service
        pedido = PedidoService.avancar_status(
            pedido_id=pedido_id,
            usuario=f'Restaurante: {usuario}'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Status avançado com sucesso',
            'pedido': {
                'id': pedido.id,
                'status': pedido.get_status_display(),
                'status_code': pedido.status
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Formato de JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao avançar status: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def _obter_detalhes_pedido(request, pedido_id):
    """View para restaurante obter detalhes completos do pedido."""
    try:
        # Verificar se é usuário do restaurante
        
        # Obter resumo completo do pedido
        resumo = PedidoService.obter_resumo_pedido(pedido_id)
        
        # Adicionar informações extras para o restaurante
        historico = PedidoService.obter_historico_pedido(pedido_id)
        estatisticas = PedidoService.calcular_estatisticas_pedido(pedido_id)
        
        return JsonResponse({
            'success': True,
            'pedido': resumo,
            'historico': [
                {
                    'id': h.id,
                    'status_anterior': h.get_status_anterior_display(),
                    'status_novo': h.get_status_novo_display(),
                    'usuario': h.usuario,
                    'observacoes': h.observacoes,
                    'data': h.created_at.isoformat()
                } for h in historico
            ],
            'estatisticas': estatisticas
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao obter detalhes do pedido: {str(e)}'
        }, status=500)


# ==================== ROTAS API ADICIONAIS ====================

@require_http_methods(["POST"])
def finalizar_pedido(request, pedido_id):
    """View para finalizar um pedido (cliente)."""
    try:
        # Verificar se cliente está autenticado
        if not getattr(request, 'is_client_authenticated', False):
            return JsonResponse({
                'success': False,
                'error': 'Cliente não autenticado'
            }, status=401)
        
        client = request.client
        
        # Verificar se o pedido pertence ao cliente
        pedido = get_object_or_404(Pedido, id=pedido_id, cliente=client)
        
        # Finalizar pedido usando o service
        pedido_finalizado = PedidoService.finalizar_pedido(
            pedido_id=pedido_id,
            usuario=f'Cliente: {client.name}'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Pedido finalizado com sucesso',
            'pedido': {
                'id': pedido_finalizado.id,
                'status': pedido_finalizado.get_status_display(),
                'tempo_estimado_entrega': pedido_finalizado.estimated_delivery_time.isoformat() if pedido_finalizado.estimated_delivery_time else None
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao finalizar pedido: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def obter_pedido(request, pedido_id):
    """View para obter detalhes de um pedido (cliente)."""
    try:
        # Verificar se cliente está autenticado
        if not getattr(request, 'is_client_authenticated', False):
            return JsonResponse({
                'success': False,
                'error': 'Cliente não autenticado'
            }, status=401)
        
        client = request.client
        
        # Verificar se o pedido pertence ao cliente
        pedido = get_object_or_404(Pedido, id=pedido_id, cliente=client)
        
        # Obter resumo do pedido
        resumo = PedidoService.obter_resumo_pedido(pedido_id)
        
        return JsonResponse({
            'success': True,
            'pedido': resumo
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao obter pedido: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def listar_pedidos_cliente(request):
    """View para listar pedidos do cliente."""
    try:
        # Verificar se cliente está autenticado
        if not getattr(request, 'is_client_authenticated', False):
            return JsonResponse({
                'success': False,
                'error': 'Cliente não autenticado'
            }, status=401)
        
        client = request.client
        
        # Parâmetros de filtro
        status_filter = request.GET.get('status')
        
        # Listar pedidos usando o service
        pedidos = PedidoService.listar_pedidos_cliente(
            cliente_id=client.id,
            status=status_filter
        )
        
        pedidos_data = []
        for pedido in pedidos:
            pedidos_data.append({
                'id': pedido.id,
                'status': {
                    'codigo': pedido.status,
                    'nome': pedido.get_status_display()
                },
                'total': float(pedido.total_price),
                'criado_em': pedido.created_at.isoformat(),
                'tempo_estimado_entrega': pedido.estimated_delivery_time.isoformat() if pedido.estimated_delivery_time else None,
                'pode_ser_cancelado': pedido.can_be_canceled()
            })
        
        return JsonResponse({
            'success': True,
            'pedidos': pedidos_data,
            'total': len(pedidos_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao listar pedidos: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def atualizar_quantidade_item(request):
    """View para atualizar quantidade de um item no pedido."""
    try:
        # Verificar se cliente está autenticado
        if not getattr(request, 'is_client_authenticated', False):
            return JsonResponse({
                'success': False,
                'error': 'Cliente não autenticado'
            }, status=401)
        
        client = request.client
        data = json.loads(request.body)
        
        # Validar dados obrigatórios
        pedido_id = data.get('pedido_id')
        produto_id = data.get('produto_id')
        nova_quantidade = data.get('quantidade')
        
        if not pedido_id or not produto_id or nova_quantidade is None:
            return JsonResponse({
                'success': False,
                'error': 'pedido_id, produto_id e quantidade são obrigatórios'
            }, status=400)
        
        if nova_quantidade < 0:
            return JsonResponse({
                'success': False,
                'error': 'Quantidade não pode ser negativa'
            }, status=400)
        
        # Verificar se o pedido pertence ao cliente
        pedido = get_object_or_404(Pedido, id=pedido_id, cliente=client)
        
        # Atualizar quantidade usando o service
        item = PedidoService.atualizar_quantidade_item(
            pedido_id=pedido_id,
            produto_id=produto_id,
            nova_quantidade=nova_quantidade
        )
        
        # Obter pedido atualizado
        pedido.refresh_from_db()
        
        response_data = {
            'success': True,
            'pedido_total': float(pedido.total_price)
        }
        
        if item:  # Item atualizado
            response_data.update({
                'message': 'Quantidade atualizada com sucesso',
                'item': {
                    'id': item.id,
                    'produto': item.produto.name,
                    'quantidade': item.quantidade,
                    'subtotal': float(item.subtotal)
                }
            })
        else:  # Item removido (quantidade = 0)
            response_data['message'] = 'Item removido com sucesso'
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Formato de JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao atualizar quantidade: {str(e)}'
        }, status=500)


# ==================== ROTAS DO RESTAURANTE ADICIONAIS ====================

@require_http_methods(["GET"])
def _listar_pedidos_por_status(request):
    """View para restaurante listar pedidos por status."""
    try:
        # Verificar se é usuário do restaurante
        
        status = request.GET.get('status')
        if not status:
            return JsonResponse({
                'success': False,
                'error': 'Parâmetro status é obrigatório'
            }, status=400)
        
        # Listar pedidos por status
        pedidos = PedidoService.listar_pedidos_por_status(status)
        
        pedidos_data = []
        for pedido in pedidos:
            pedidos_data.append({
                'id': pedido.id,
                'cliente': {
                    'id': pedido.cliente.id,
                    'nome': pedido.cliente.name,
                    'telefone': pedido.cliente.phone
                },
                'status': {
                    'codigo': pedido.status,
                    'nome': pedido.get_status_display()
                },
                'total': float(pedido.total_price),
                'criado_em': pedido.created_at.isoformat(),
                'tempo_estimado_entrega': pedido.estimated_delivery_time.isoformat() if pedido.estimated_delivery_time else None,
                'endereco_entrega': pedido.delivery_address,
                'observacoes': pedido.notes
            })
        
        return JsonResponse({
            'success': True,
            'pedidos': pedidos_data,
            'total': len(pedidos_data),
            'status_consultado': status
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao listar pedidos: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def _obter_estatisticas_pedido(request, pedido_id):
    """View para restaurante obter estatísticas de um pedido."""
    try:
        # Verificar se é usuário do restaurante
        
        # Obter estatísticas do pedido
        estatisticas = PedidoService.calcular_estatisticas_pedido(pedido_id)
        
        return JsonResponse({
            'success': True,
            'estatisticas': estatisticas
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao obter estatísticas: {str(e)}'
        }, status=500)
    