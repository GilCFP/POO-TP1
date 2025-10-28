from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from typing import List, Dict, Optional, Any

from ..models import Pedido, ItemPedido, StatusPedido, HistoricoPedido
from apps.cliente.models import Cliente
from apps.produto.models import Produto


class PedidoService:
    """Serviço para gerenciar operações relacionadas a pedidos."""
    
    @staticmethod
    def criar_pedido(cliente_id: int, delivery_address: str = '', notes: str = '', usuario: str = 'Sistema') -> Pedido:
        """
        Cria um novo pedido para um cliente.
        
        Args:
            cliente_id: ID do cliente
            delivery_address: Endereço de entrega (opcional)
            notes: Observações para o pedido (opcional)
            payment_method: Método de pagamento (opcional)
            usuario: Usuário que está criando o pedido (opcional)
            
        Returns:
            Pedido criado
            
        Raises:
            ValidationError: Se o cliente não existir ou dados inválidos
        """
        try:
            cliente = Cliente.objects.get(id=cliente_id)
        except Cliente.DoesNotExist:
            raise ValidationError("Cliente não encontrado")
        
        with transaction.atomic():
            pedido = Pedido.objects.create(
                cliente=cliente,
                delivery_address=delivery_address,
                notes=notes,
            )
            
            # Log inicial no histórico
            HistoricoPedido.objects.create(
                pedido=pedido,
                status_anterior='',
                status_novo=StatusPedido.ORDERING,
                usuario=usuario,
                observacoes='Pedido criado'
            )
            
        return pedido
    
    @staticmethod
    def adicionar_item(pedido_id: int, produto_id: int, quantidade: int = 1, 
                      instrucoes_especiais: str = '') -> ItemPedido:
        """
        Adiciona um item ao pedido.
        
        Args:
            pedido_id: ID do pedido
            produto_id: ID do produto
            quantidade: Quantidade do produto
            instrucoes_especiais: Instruções especiais para o item
            
        Returns:
            ItemPedido criado ou atualizado
            
        Raises:
            ValidationError: Se pedido ou produto não existir, ou pedido não permitir modificação
        """
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            produto = Produto.objects.get(id=produto_id)
        except Pedido.DoesNotExist:
            raise ValidationError("Pedido não encontrado")
        except Produto.DoesNotExist:
            raise ValidationError("Produto não encontrado")
        
        if pedido.status != StatusPedido.ORDERING:
            raise ValidationError("Não é possível modificar um pedido que não está sendo montado")
        
        if quantidade <= 0:
            raise ValidationError("Quantidade deve ser maior que zero")
        
        with transaction.atomic():
            item, created = ItemPedido.objects.get_or_create(
                pedido=pedido,
                produto=produto,
                defaults={
                    'quantidade': quantidade,
                    'special_instructions': instrucoes_especiais
                }
            )
            
            if not created:
                item.quantidade += quantidade
                if instrucoes_especiais:
                    item.special_instructions = instrucoes_especiais
                item.save()
            
            pedido.calculate_total()
            
        return item
    
    @staticmethod
    def remover_item(pedido_id: int, produto_id: int) -> bool:
        """
        Remove um item do pedido.
        
        Args:
            pedido_id: ID do pedido
            produto_id: ID do produto
            
        Returns:
            True se removido com sucesso
            
        Raises:
            ValidationError: Se pedido não permitir modificação ou item não existir
        """
        try:
            pedido = Pedido.objects.get(id=pedido_id)
        except Pedido.DoesNotExist:
            raise ValidationError("Pedido não encontrado")
        
        if pedido.status != StatusPedido.ORDERING:
            raise ValidationError("Não é possível modificar um pedido que não está sendo montado")
        
        try:
            with transaction.atomic():
                item = ItemPedido.objects.get(pedido=pedido, produto_id=produto_id)
                item.delete()
                pedido.calculate_total()
                return True
        except ItemPedido.DoesNotExist:
            raise ValidationError("Item não encontrado no pedido")
    
    @staticmethod
    def atualizar_quantidade_item(pedido_id: int, produto_id: int, nova_quantidade: int) -> ItemPedido:
        """
        Atualiza a quantidade de um item no pedido.
        
        Args:
            pedido_id: ID do pedido
            produto_id: ID do produto
            nova_quantidade: Nova quantidade (0 para remover)
            
        Returns:
            ItemPedido atualizado ou None se removido
        """
        if nova_quantidade == 0:
            PedidoService.remover_item(pedido_id, produto_id)
            return None
        
        try:
            pedido = Pedido.objects.get(id=pedido_id)
        except Pedido.DoesNotExist:
            raise ValidationError("Pedido não encontrado")
        
        if pedido.status != StatusPedido.ORDERING:
            raise ValidationError("Não é possível modificar um pedido que não está sendo montado")
        
        try:
            with transaction.atomic():
                item = ItemPedido.objects.get(pedido=pedido, produto_id=produto_id)
                item.quantidade = nova_quantidade
                item.save()
                pedido.calculate_total()
                return item
        except ItemPedido.DoesNotExist:
            raise ValidationError("Item não encontrado no pedido")
    
    @staticmethod
    def mudar_status(pedido_id: int, novo_status: str, usuario: str = 'Sistema', 
                    observacoes: str = '') -> Pedido:
        """
        Muda o status do pedido com validações e registro no histórico.
        
        Args:
            pedido_id: ID do pedido
            novo_status: Novo status do pedido
            usuario: Usuário que está fazendo a alteração
            observacoes: Observações sobre a mudança
            
        Returns:
            Pedido com status atualizado
        """
        try:
            pedido = Pedido.objects.get(id=pedido_id)
        except Pedido.DoesNotExist:
            raise ValidationError("Pedido não encontrado")
        
        status_anterior = pedido.status
        
        with transaction.atomic():
            # Usar o método do modelo que já tem as validações
            pedido.change_status(novo_status)
            
            # Registrar no histórico
            HistoricoPedido.objects.create(
                pedido=pedido,
                status_anterior=status_anterior,
                status_novo=novo_status,
                usuario=usuario,
                observacoes=observacoes
            )
            
            # Associar automaticamente à cozinha quando o status for WAITING
            PedidoService._associar_pedido_cozinha(pedido)
        
        return pedido
    
    @staticmethod
    def avancar_status(pedido_id: int, usuario: str = 'Sistema') -> Pedido:
        """
        Avança o pedido para o próximo status automaticamente.
        
        Args:
            pedido_id: ID do pedido
            usuario: Usuário que está fazendo a alteração
            
        Returns:
            Pedido com status atualizado
        """
        try:
            pedido = Pedido.objects.get(id=pedido_id)
        except Pedido.DoesNotExist:
            raise ValidationError("Pedido não encontrado")
        
        status_anterior = pedido.status
        
        with transaction.atomic():
            pedido.go_to_next_status()
            
            # Registrar no histórico
            HistoricoPedido.objects.create(
                pedido=pedido,
                status_anterior=status_anterior,
                status_novo=pedido.status,
                usuario=usuario,
                observacoes='Status avançado automaticamente'
            )
            
            # Associar automaticamente à cozinha quando necessário
            PedidoService._associar_pedido_cozinha(pedido)
        
        return pedido
    
    @staticmethod
    def cancelar_pedido(pedido_id: int, motivo: str = '', usuario: str = 'Sistema') -> Pedido:
        """
        Cancela um pedido se possível.
        
        Args:
            pedido_id: ID do pedido
            motivo: Motivo do cancelamento
            usuario: Usuário que está cancelando
            
        Returns:
            Pedido cancelado
            
        Raises:
            ValidationError: Se o pedido não puder ser cancelado
        """
        try:
            pedido = Pedido.objects.get(id=pedido_id)
        except Pedido.DoesNotExist:
            raise ValidationError("Pedido não encontrado")
        
        if not pedido.can_be_canceled():
            raise ValidationError("Este pedido não pode ser cancelado no status atual")
        
        return PedidoService.mudar_status(
            pedido_id, 
            StatusPedido.CANCELED, 
            usuario, 
            f"Cancelamento: {motivo}"
        )
    
    @staticmethod
    def finalizar_pedido(pedido_id: int, usuario: str = 'Sistema') -> Pedido:
        """
        Finaliza um pedido (muda para aguardando pagamento).
        
        Args:
            pedido_id: ID do pedido
            usuario: Usuário que está finalizando
            
        Returns:
            Pedido finalizado
        """
        try:
            pedido = Pedido.objects.get(id=pedido_id)
        except Pedido.DoesNotExist:
            raise ValidationError("Pedido não encontrado")
        
        if not pedido.items.exists():
            raise ValidationError("Não é possível finalizar um pedido sem itens")
        
        # Calcular tempo estimado de entrega
        tempo_preparo = pedido.get_estimated_prep_time()
        pedido.estimated_delivery_time = timezone.now() + timedelta(minutes=tempo_preparo)
        pedido.save()
        
        return PedidoService.mudar_status(
            pedido_id, 
            StatusPedido.PENDING_PAYMENT, 
            usuario, 
            'Pedido finalizado'
        )
    
    @staticmethod
    def obter_resumo_pedido(pedido_id: int) -> Dict[str, Any]:
        """
        Obtém um resumo completo do pedido.
        
        Args:
            pedido_id: ID do pedido
            
        Returns:
            Dicionário com informações do pedido
        """
        try:
            pedido = Pedido.objects.select_related('cliente').prefetch_related(
                'itempedido_set__produto'
            ).get(id=pedido_id)
        except Pedido.DoesNotExist:
            raise ValidationError("Pedido não encontrado")
        
        return {
            'id': pedido.id,
            'cliente': {
                'id': pedido.cliente.id,
                'nome': pedido.cliente.name,
                'email': getattr(pedido.cliente, 'email', ''),
            },
            'status': {
                'codigo': pedido.status,
                'nome': pedido.get_status_display()
            },
            'itens': pedido.get_items_summary(),
            'total': float(pedido.total_price),
            'endereco_entrega': pedido.delivery_address,
            'tempo_estimado_entrega': pedido.estimated_delivery_time,
            'metodo_pagamento': pedido.payment_method,
            'observacoes': pedido.notes,
            'tempo_preparo_estimado': pedido.get_estimated_prep_time(),
            'total_calorias': pedido.get_total_calories(),
            'pode_ser_cancelado': pedido.can_be_canceled(),
            'criado_em': pedido.created_at,
            'atualizado_em': pedido.updated_at
        }
    
    @staticmethod
    def listar_pedidos_cliente(cliente_id: int, status: Optional[str] = None) -> List[Pedido]:
        """
        Lista pedidos de um cliente, opcionalmente filtrados por status.
        
        Args:
            cliente_id: ID do cliente
            status: Status específico para filtrar (opcional)
            
        Returns:
            Lista de pedidos
        """
        queryset = Pedido.objects.filter(cliente_id=cliente_id).select_related('cliente')
        
        if status:
            queryset = queryset.filter(status=status)
        
        return list(queryset.order_by('-created_at'))
    
    @staticmethod
    def listar_pedidos_por_status(status: str) -> List[Pedido]:
        """
        Lista todos os pedidos com um status específico.
        
        Args:
            status: Status dos pedidos
            
        Returns:
            Lista de pedidos
        """
        return list(
            Pedido.objects.filter(status=status)
            .select_related('cliente')
            .order_by('created_at')
        )
    
    @staticmethod
    def obter_historico_pedido(pedido_id: int) -> List[HistoricoPedido]:
        """
        Obtém o histórico de mudanças de status de um pedido.
        
        Args:
            pedido_id: ID do pedido
            
        Returns:
            Lista do histórico ordenada por data
        """
        return list(
            HistoricoPedido.objects.filter(pedido_id=pedido_id)
            .order_by('created_at')
        )
    
    @staticmethod
    def calcular_estatisticas_pedido(pedido_id: int) -> Dict[str, Any]:
        """
        Calcula estatísticas nutricionais e outras informações do pedido.
        
        Args:
            pedido_id: ID do pedido
            
        Returns:
            Dicionário com estatísticas
        """
        try:
            pedido = Pedido.objects.prefetch_related(
                'itempedido_set__produto'
            ).get(id=pedido_id)
        except Pedido.DoesNotExist:
            raise ValidationError("Pedido não encontrado")
        
        total_itens = sum(item.quantidade for item in pedido.itempedido_set.all())
        restricoes_alimentares = set()
        
        # Coleta restrições alimentares de todos os itens
        for item in pedido.itempedido_set.all():
            if hasattr(item.produto, 'alimento'):
                restricoes = item.produto.alimento.alimentary_restrictions.values_list('name', flat=True)
                restricoes_alimentares.update(restricoes)
        
        return {
            'total_itens': total_itens,
            'total_calorias': pedido.get_total_calories(),
            'tempo_preparo_estimado': pedido.get_estimated_prep_time(),
            'restricoes_alimentares': list(restricoes_alimentares),
            'valor_medio_por_item': float(pedido.total_price / total_itens) if total_itens > 0 else 0,
        }
    
    @staticmethod
    def processar_pagamento(pedido_id: int, metodo_pagamento: str = None, 
                           usuario: str = 'Sistema') -> Pedido:
        """
        Processa o pagamento de um pedido.
        
        Args:
            pedido_id: ID do pedido
            metodo_pagamento: Método de pagamento (opcional, usa o do pedido se não informado)
            usuario: Usuário que está processando
            
        Returns:
            Pedido com pagamento processado
        """
        try:
            pedido = Pedido.objects.get(id=pedido_id)
        except Pedido.DoesNotExist:
            raise ValidationError("Pedido não encontrado")
        
        if pedido.status != StatusPedido.PENDING_PAYMENT:
            raise ValidationError("Pedido não está aguardando pagamento")
        
        if metodo_pagamento:
            pedido.payment_method = metodo_pagamento
            pedido.save()
        
        # Aqui seria implementada a lógica real de pagamento
        # Por enquanto, apenas avança o status
        return PedidoService.mudar_status(
            pedido_id,
            StatusPedido.WAITING,
            usuario,
            f"Pagamento processado via {pedido.payment_method}"
        )
    
    @staticmethod
    def _associar_pedido_cozinha(pedido: Pedido) -> None:
        """
        Associa automaticamente um pedido à cozinha baseado no seu status.
        
        Args:
            pedido: Instância do pedido
        """
        try:
            from apps.restaurante.models import Cozinha
            
            # Buscar a primeira cozinha ativa
            cozinha = Cozinha.objects.filter(is_active=True).first()
            if not cozinha:
                return  # Se não há cozinha ativa, não faz nada
            
            # Remover o pedido de todos os relacionamentos primeiro (sem gerar erro se não existir)
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
            
            # Associar ao relacionamento correto baseado no status
            if pedido.status == StatusPedido.WAITING:
                cozinha.orders_in_queue.add(pedido)
            elif pedido.status == StatusPedido.PREPARING:
                cozinha.orders_in_progress.add(pedido)
            elif pedido.status == StatusPedido.READY:
                cozinha.orders_ready.add(pedido)
            # Para outros status (BEING_DELIVERED, DELIVERED, etc.), não associa
            
        except Exception as e:
            # Log do erro mas não falha a operação principal
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Erro ao associar pedido #{pedido.id} à cozinha: {e}")
            pass
