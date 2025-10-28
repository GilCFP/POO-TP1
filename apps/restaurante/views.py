from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.conf import settings
import json
import logging

from .models import Cozinha, Restaurante
from apps.pedido.models import StatusPedido, Pedido
from apps.pedido.services.pedido_service import PedidoService

# Configure logging
logger = logging.getLogger(__name__)


class BaseKanbanAPIView(TemplateView):
    """Classe base para views da API do kanban com tratamento de erros padronizado."""
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch para adicionar validações gerais."""
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Erro não tratado na API do kanban: {str(e)}", exc_info=True)
            return self._error_response(
                "Erro interno do servidor",
                status=500,
                details=str(e) if settings.DEBUG else None
            )
    
    def _error_response(self, message, status=400, details=None, error_code=None):
        """Cria uma resposta de erro padronizada."""
        response_data = {
            'success': False,
            'error': message,
            'timestamp': timezone.now().isoformat()
        }
        
        if details:
            response_data['details'] = details
        
        if error_code:
            response_data['error_code'] = error_code
            
        return JsonResponse(response_data, status=status)
    
    def _success_response(self, data=None, message=None):
        """Cria uma resposta de sucesso padronizada."""
        response_data = {
            'success': True,
            'timestamp': timezone.now().isoformat()
        }
        
        if data:
            response_data.update(data)
        
        if message:
            response_data['message'] = message
            
        return JsonResponse(response_data)
    
    def _validate_json_request(self, request):
        """Valida e parse o JSON do request."""
        if request.content_type != 'application/json':
            raise ValidationError("Content-Type deve ser application/json")
        
        try:
            return json.loads(request.body)
        except json.JSONDecodeError as e:
            raise ValidationError(f"JSON inválido: {str(e)}")
    
    def _validate_pedido_exists(self, pedido_id):
        """Valida se o pedido existe e retorna o objeto."""
        try:
            return Pedido.objects.get(id=pedido_id)
        except Pedido.DoesNotExist:
            raise ValidationError(f"Pedido #{pedido_id} não encontrado")
    
    def _validate_status_transition(self, pedido, novo_status):
        """Valida se a transição de status é permitida."""
        # Status que não podem ser alterados
        immutable_statuses = [StatusPedido.CANCELED, StatusPedido.DELIVERED]
        if pedido.status in immutable_statuses:
            raise ValidationError(f"Não é possível alterar status de pedido {pedido.get_status_display()}")
        
        # Validações específicas por status
        if novo_status == StatusPedido.PREPARING and pedido.status != StatusPedido.WAITING:
            raise ValidationError("Pedido deve estar 'Aguardando' para ser movido para 'Preparando'")
        
        if novo_status == StatusPedido.READY and pedido.status != StatusPedido.PREPARING:
            raise ValidationError("Pedido deve estar 'Preparando' para ser movido para 'Pronto'")
        
        if novo_status == StatusPedido.BEING_DELIVERED and pedido.status != StatusPedido.READY:
            raise ValidationError("Pedido deve estar 'Pronto' para ser movido para 'Sendo Entregue'")
        
        # Não permitir voltar status (exceto para cancelamento)
        status_order = {
            StatusPedido.ORDERING: 0,
            StatusPedido.PENDING_PAYMENT: 1,
            StatusPedido.WAITING: 2,
            StatusPedido.PREPARING: 3,
            StatusPedido.READY: 4,
            StatusPedido.BEING_DELIVERED: 5,
            StatusPedido.DELIVERED: 6
        }
        
        current_order = status_order.get(pedido.status, 0)
        new_order = status_order.get(novo_status, 0)
        
        if new_order < current_order and novo_status != StatusPedido.CANCELED:
            raise ValidationError("Não é possível voltar para um status anterior")
    
    def _get_cozinha(self):
        """Obtém a cozinha ativa ou levanta erro."""
        cozinha = Cozinha.objects.select_related('restaurante').first()
        if not cozinha:
            raise ValidationError("Nenhuma cozinha configurada no sistema")
        if not cozinha.is_active:
            raise ValidationError("Cozinha não está ativa")
        return cozinha


class KanbanView(TemplateView):
    """View principal para o kanban da cozinha."""
    template_name = 'restaurante/kanban.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Buscar a cozinha (assumindo que há apenas uma por enquanto)
        try:
            cozinha = Cozinha.objects.select_related('restaurante').first()
            if not cozinha:
                # Se não há cozinha, criar dados vazios
                context.update({
                    'orders_by_status': {},
                    'status_choices': StatusPedido.choices,
                    'cozinha_info': None,
                    'initial_data': json.dumps({
                        'orders_by_status': {},
                        'status_choices': [{'codigo': code, 'nome': name} for code, name in StatusPedido.choices]
                    })
                })
                return context
            
            # Buscar pedidos agrupados por status
            orders_by_status = {}
            
            # Status para o kanban (excluindo alguns status)
            kanban_statuses = [
                (StatusPedido.WAITING, 'Aguardando'),
                (StatusPedido.PREPARING, 'Preparando'), 
                (StatusPedido.READY, 'Pronto'),
                (StatusPedido.BEING_DELIVERED, 'Sendo Entregue')
            ]
            
            for status_code, status_name in kanban_statuses:
                if status_code == StatusPedido.WAITING:
                    orders = cozinha.orders_in_queue.select_related('cliente').prefetch_related('itempedido_set__produto').all()
                elif status_code == StatusPedido.PREPARING:
                    orders = cozinha.orders_in_progress.select_related('cliente').prefetch_related('itempedido_set__produto').all()
                elif status_code == StatusPedido.READY:
                    orders = cozinha.orders_ready.select_related('cliente').prefetch_related('itempedido_set__produto').all()
                elif status_code == StatusPedido.BEING_DELIVERED:
                    # Para pedidos sendo entregues, buscar diretamente do modelo Pedido
                    orders = Pedido.objects.filter(
                        status=StatusPedido.BEING_DELIVERED
                    ).select_related('cliente').prefetch_related('itempedido_set__produto').all()
                else:
                    orders = []
                
                # Formatar dados dos pedidos
                formatted_orders = []
                for order in orders:
                    order_data = {
                        'id': order.id,
                        'cliente': {
                            'nome': order.cliente.name if order.cliente else 'Cliente não informado',
                            'telefone': getattr(order.cliente, 'phone', '') if order.cliente else ''
                        },
                        'total': float(order.total_price),
                        'criado_em': order.created_at.isoformat() if order.created_at else '',
                        'endereco_entrega': order.delivery_address or '',
                        'observacoes': order.notes or '',
                        'items': []
                    }
                    
                    # Adicionar itens do pedido
                    for item in order.itempedido_set.all():
                        item_data = {
                            'id': item.id,
                            'quantidade': item.quantidade,
                            'produto_nome': item.produto.name if item.produto else 'Produto não encontrado'
                        }
                        order_data['items'].append(item_data)
                    
                    formatted_orders.append(order_data)
                
                orders_by_status[status_code] = {
                    'name': status_name,
                    'orders': formatted_orders,
                    'total': len(formatted_orders)
                }
            
            # Preparar dados para o contexto
            context.update({
                'orders_by_status': orders_by_status,
                'status_choices': StatusPedido.choices,
                'cozinha_info': {
                    'id': cozinha.id,
                    'restaurante_nome': cozinha.restaurante.name,
                    'capacidade_total': cozinha.full_capacity,
                    'capacidade_atual': cozinha.current_capacity_usage,
                    'capacidade_disponivel': cozinha.available_capacity
                },
                'initial_data': json.dumps({
                    'orders_by_status': orders_by_status,
                    'status_choices': [{'codigo': code, 'nome': name} for code, name in StatusPedido.choices],
                    'cozinha_info': {
                        'id': cozinha.id,
                        'restaurante_nome': cozinha.restaurante.name,
                        'capacidade_total': cozinha.full_capacity,
                        'capacidade_atual': cozinha.current_capacity_usage,
                        'capacidade_disponivel': cozinha.available_capacity
                    }
                })
            })
            
        except Exception as e:
            # Em caso de erro, retornar dados vazios
            context.update({
                'orders_by_status': {},
                'status_choices': StatusPedido.choices,
                'cozinha_info': None,
                'initial_data': json.dumps({
                    'orders_by_status': {},
                    'status_choices': [{'codigo': code, 'nome': name} for code, name in StatusPedido.choices],
                    'error': str(e)
                })
            })
        
        return context


class KanbanAPIView(BaseKanbanAPIView):
    """API view para dados do kanban."""
    
    def get(self, request, *args, **kwargs):
        """Retorna dados atuais dos pedidos para o kanban."""
        try:
            # Buscar a cozinha
            cozinha = self._get_cozinha()
            
            # Buscar pedidos agrupados por status
            orders_by_status = self._get_orders_by_status(cozinha)
            
            return self._success_response({
                'orders_by_status': orders_by_status,
                'status_choices': [{'codigo': code, 'nome': name} for code, name in StatusPedido.choices],
                'cozinha_info': {
                    'id': cozinha.id,
                    'restaurante_nome': cozinha.restaurante.name,
                    'capacidade_total': cozinha.full_capacity,
                    'capacidade_atual': cozinha.current_capacity_usage,
                    'capacidade_disponivel': cozinha.available_capacity
                }
            })
            
        except ValidationError as e:
            return self._error_response(str(e), status=400)
        except Exception as e:
            logger.error(f"Erro ao buscar dados do kanban: {str(e)}", exc_info=True)
            return self._error_response(
                "Erro ao carregar dados do kanban",
                status=500,
                details=str(e) if settings.DEBUG else None
            )
    
    def _get_orders_by_status(self, cozinha):
        """Busca e formata pedidos agrupados por status."""
        orders_by_status = {}
        
        # Status para o kanban (excluindo alguns status)
        kanban_statuses = [
            (StatusPedido.WAITING, 'Aguardando'),
            (StatusPedido.PREPARING, 'Preparando'), 
            (StatusPedido.READY, 'Pronto'),
            (StatusPedido.BEING_DELIVERED, 'Sendo Entregue')
        ]
        
        for status_code, status_name in kanban_statuses:
            if status_code == StatusPedido.WAITING:
                orders = cozinha.orders_in_queue.select_related('cliente').prefetch_related('itempedido_set__produto').all()
            elif status_code == StatusPedido.PREPARING:
                orders = cozinha.orders_in_progress.select_related('cliente').prefetch_related('itempedido_set__produto').all()
            elif status_code == StatusPedido.READY:
                orders = cozinha.orders_ready.select_related('cliente').prefetch_related('itempedido_set__produto').all()
            elif status_code == StatusPedido.BEING_DELIVERED:
                # Para pedidos sendo entregues, buscar diretamente do modelo Pedido
                orders = Pedido.objects.filter(
                    status=StatusPedido.BEING_DELIVERED
                ).select_related('cliente').prefetch_related('itempedido_set__produto').all()
            else:
                orders = []
            
            # Formatar dados dos pedidos
            formatted_orders = []
            for order in orders:
                order_data = self._format_order_data(order)
                formatted_orders.append(order_data)
            
            orders_by_status[status_code] = {
                'name': status_name,
                'orders': formatted_orders,
                'total': len(formatted_orders)
            }
        
        return orders_by_status
    
    def _format_order_data(self, order):
        """Formata dados de um pedido para a resposta da API."""
        return {
            'id': order.id,
            'cliente': {
                'nome': order.cliente.name if order.cliente else 'Cliente não informado',
                'telefone': getattr(order.cliente, 'phone', '') if order.cliente else ''
            },
            'total': float(order.total_price),
            'criado_em': order.created_at.isoformat() if order.created_at else '',
            'endereco_entrega': order.delivery_address or '',
            'observacoes': order.notes or '',
            'items': [
                {
                    'id': item.id,
                    'quantidade': item.quantidade,
                    'produto_nome': item.produto.name if item.produto else 'Produto não encontrado',
                    'preco_unitario': float(item.unit_price),
                    'subtotal': float(item.subtotal),
                    'instrucoes_especiais': item.special_instructions or ''
                }
                for item in order.itempedido_set.all()
            ]
        }


@method_decorator(csrf_exempt, name='dispatch')
class KanbanStatusUpdateAPIView(BaseKanbanAPIView):
    """API view para atualizar status de pedidos no kanban."""
    
    def post(self, request, pedido_id, *args, **kwargs):
        """Atualiza o status de um pedido específico."""
        try:
            # Validar e parse do JSON do request
            data = self._validate_json_request(request)
            novo_status = data.get('status')
            
            if not novo_status:
                return self._error_response('Campo "status" é obrigatório', error_code='MISSING_STATUS')
            
            # Validar se o status é válido
            valid_statuses = [choice[0] for choice in StatusPedido.choices]
            if novo_status not in valid_statuses:
                return self._error_response(
                    f'Status "{novo_status}" inválido. Status válidos: {", ".join(valid_statuses)}',
                    error_code='INVALID_STATUS'
                )
            
            # Validar se o pedido existe
            pedido = self._validate_pedido_exists(pedido_id)
            
            # Validar transição de status
            self._validate_status_transition(pedido, novo_status)
            
            # Usar transação para garantir consistência
            with transaction.atomic():
                # Usar o PedidoService para atualizar o status
                usuario = getattr(request.user, 'username', 'Sistema')
                pedido = PedidoService.mudar_status(
                    pedido_id=pedido_id,
                    novo_status=novo_status,
                    usuario=usuario,
                    observacoes=f'Status alterado via kanban para {StatusPedido(novo_status).label}'
                )
                
                # Atualizar relacionamentos da cozinha se necessário
                self._update_kitchen_relationships(pedido)
            
            return self._success_response(
                data={
                    'pedido': {
                        'id': pedido.id,
                        'status': pedido.status,
                        'status_display': pedido.get_status_display()
                    }
                },
                message=f'Status do pedido #{pedido.id} atualizado para {pedido.get_status_display()}'
            )
            
        except ValidationError as e:
            return self._error_response(str(e), error_code='VALIDATION_ERROR')
        except IntegrityError as e:
            logger.error(f"Erro de integridade ao atualizar status: {str(e)}", exc_info=True)
            return self._error_response(
                "Erro de consistência de dados",
                status=409,
                error_code='INTEGRITY_ERROR'
            )
        except Exception as e:
            logger.error(f"Erro ao atualizar status do pedido {pedido_id}: {str(e)}", exc_info=True)
            return self._error_response(
                "Erro interno ao atualizar status",
                status=500,
                details=str(e) if settings.DEBUG else None,
                error_code='INTERNAL_ERROR'
            )
    
    def _update_kitchen_relationships(self, pedido):
        """Atualiza os relacionamentos ManyToMany da cozinha baseado no status do pedido."""
        try:
            cozinha = self._get_cozinha()
            
            # Remover o pedido de todos os relacionamentos primeiro (sem falhar se não existir)
            try:
                cozinha.orders_in_queue.remove(pedido)
            except:
                pass
            try:
                cozinha.orders_in_progress.remove(pedido)
            except:
                pass
            try:
                cozinha.orders_ready.remove(pedido)
            except:
                pass
            
            # Adicionar ao relacionamento correto baseado no status
            if pedido.status == StatusPedido.WAITING:
                cozinha.orders_in_queue.add(pedido)
                logger.info(f"Pedido #{pedido.id} adicionado à fila da cozinha")
            elif pedido.status == StatusPedido.PREPARING:
                cozinha.orders_in_progress.add(pedido)
                logger.info(f"Pedido #{pedido.id} movido para em progresso na cozinha")
            elif pedido.status == StatusPedido.READY:
                cozinha.orders_ready.add(pedido)
                logger.info(f"Pedido #{pedido.id} marcado como pronto na cozinha")
            # Para BEING_DELIVERED e outros, não adicionar a nenhum relacionamento
            
        except ValidationError:
            # Re-raise validation errors (cozinha não encontrada, etc.)
            raise
        except Exception as e:
            # Log do erro, mas não falhar a operação principal
            logger.warning(f"Erro ao atualizar relacionamentos da cozinha para pedido #{pedido.id}: {e}")
            # Não re-raise para não quebrar a operação principal


@method_decorator(csrf_exempt, name='dispatch')
class KanbanAdvanceStatusAPIView(BaseKanbanAPIView):
    """API view para avançar pedidos para o próximo status automaticamente."""
    
    def post(self, request, pedido_id, *args, **kwargs):
        """Avança um pedido para o próximo status na sequência."""
        try:
            # Validar se o pedido existe
            pedido = self._validate_pedido_exists(pedido_id)
            
            # Validar se o pedido pode ser avançado
            if pedido.status == StatusPedido.DELIVERED:
                return self._error_response(
                    "Pedido já foi entregue e não pode ser avançado",
                    error_code='ALREADY_DELIVERED'
                )
            
            if pedido.status == StatusPedido.CANCELED:
                return self._error_response(
                    "Pedido cancelado não pode ser avançado",
                    error_code='CANCELED_ORDER'
                )
            
            # Usar transação para garantir consistência
            with transaction.atomic():
                # Usar o PedidoService para avançar o status
                usuario = getattr(request.user, 'username', 'Sistema')
                pedido = PedidoService.avancar_status(
                    pedido_id=pedido_id,
                    usuario=usuario
                )
                
                # Atualizar relacionamentos da cozinha se necessário
                self._update_kitchen_relationships(pedido)
            
            return self._success_response(
                data={
                    'pedido': {
                        'id': pedido.id,
                        'status': pedido.status,
                        'status_display': pedido.get_status_display()
                    }
                },
                message=f'Pedido #{pedido.id} avançado para {pedido.get_status_display()}'
            )
            
        except ValidationError as e:
            return self._error_response(str(e), error_code='VALIDATION_ERROR')
        except IntegrityError as e:
            logger.error(f"Erro de integridade ao avançar status: {str(e)}", exc_info=True)
            return self._error_response(
                "Erro de consistência de dados",
                status=409,
                error_code='INTEGRITY_ERROR'
            )
        except Exception as e:
            logger.error(f"Erro ao avançar status do pedido {pedido_id}: {str(e)}", exc_info=True)
            return self._error_response(
                "Erro interno ao avançar status",
                status=500,
                details=str(e) if settings.DEBUG else None,
                error_code='INTERNAL_ERROR'
            )
    
    def _update_kitchen_relationships(self, pedido):
        """Atualiza os relacionamentos ManyToMany da cozinha baseado no status do pedido."""
        try:
            cozinha = self._get_cozinha()
            
            # Remover o pedido de todos os relacionamentos primeiro (sem falhar se não existir)
            try:
                cozinha.orders_in_queue.remove(pedido)
            except:
                pass
            try:
                cozinha.orders_in_progress.remove(pedido)
            except:
                pass
            try:
                cozinha.orders_ready.remove(pedido)
            except:
                pass
            
            # Adicionar ao relacionamento correto baseado no status
            if pedido.status == StatusPedido.WAITING:
                cozinha.orders_in_queue.add(pedido)
                logger.info(f"Pedido #{pedido.id} adicionado à fila da cozinha")
            elif pedido.status == StatusPedido.PREPARING:
                cozinha.orders_in_progress.add(pedido)
                logger.info(f"Pedido #{pedido.id} movido para em progresso na cozinha")
            elif pedido.status == StatusPedido.READY:
                cozinha.orders_ready.add(pedido)
                logger.info(f"Pedido #{pedido.id} marcado como pronto na cozinha")
            # Para BEING_DELIVERED e outros, não adicionar a nenhum relacionamento
            
        except ValidationError:
            # Re-raise validation errors (cozinha não encontrada, etc.)
            raise
        except Exception as e:
            # Log do erro, mas não falhar a operação principal
            logger.warning(f"Erro ao atualizar relacionamentos da cozinha para pedido #{pedido.id}: {e}")
            # Não re-raise para não quebrar a operação principal


# Placeholder views - implementar conforme necessário
def restaurante_list(request):
    return JsonResponse({'message': 'Restaurante list view'})
