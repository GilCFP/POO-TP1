"""
Tasks assíncronas para operações que podem demorar ou precisam ser executadas em background.
Este arquivo é opcional e requer Celery configurado.
Para usar, instale: pip install celery redis
"""
# from celery import shared_task  # Descomentante quando instalar celery
from django.core.mail import send_mail
from django.conf import settings
from .services.business_services import ProdutoService
from .models import Pedido, StatusPedido
import logging

logger = logging.getLogger(__name__)


# @shared_task  # Descomente quando instalar celery
def verificar_produtos_vencidos():
    """Task para verificar e desativar produtos vencidos automaticamente."""
    try:
        produtos_desativados = ProdutoService.desativar_produtos_vencidos()
        logger.info(f"Verificação automática: {produtos_desativados} produtos vencidos desativados.")
        return f"Produtos desativados: {produtos_desativados}"
    except Exception as e:
        logger.error(f"Erro ao verificar produtos vencidos: {str(e)}")
        return f"Erro: {str(e)}"


# @shared_task  # Descomente quando instalar celery
def processar_entrega_pedido(pedido_id):
    """Task para simular o processo de entrega de um pedido."""
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        
        if pedido.status != StatusPedido.READY:
            return f"Pedido {pedido_id} não está pronto para entrega"
        
        # Simular tempo de entrega
        import time
        time.sleep(5)  # Simula 5 segundos de "entrega"
        
        # Atualizar status
        pedido.status = StatusPedido.BEING_DELIVERED
        pedido.save()
        
        # Simular mais tempo
        time.sleep(10)  # Simula mais 10 segundos
        
        # Finalizar entrega
        pedido.status = StatusPedido.DELIVERED
        pedido.save()
        
        logger.info(f"Pedido {pedido_id} entregue com sucesso")
        return f"Pedido {pedido_id} entregue"
        
    except Pedido.DoesNotExist:
        logger.error(f"Pedido {pedido_id} não encontrado")
        return f"Pedido {pedido_id} não encontrado"
    except Exception as e:
        logger.error(f"Erro ao processar entrega do pedido {pedido_id}: {str(e)}")
        return f"Erro: {str(e)}"


# @shared_task  # Descomente quando instalar celery
def enviar_notificacao_pedido_pronto(pedido_id):
    """Task para enviar notificação quando pedido estiver pronto."""
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        
        # Simular envio de notificação (email, SMS, push notification, etc.)
        logger.info(f"Notificação enviada: Pedido {pedido_id} está pronto para {pedido.cliente.name}")
        
        # Se tiver email configurado, pode enviar email real:
        # send_mail(
        #     'Seu pedido está pronto!',
        #     f'Olá {pedido.cliente.name}, seu pedido #{pedido.id} está pronto para retirada!',
        #     settings.DEFAULT_FROM_EMAIL,
        #     [pedido.cliente.email],  # assumindo que cliente tem email
        #     fail_silently=False,
        # )
        
        return f"Notificação enviada para pedido {pedido_id}"
        
    except Pedido.DoesNotExist:
        logger.error(f"Pedido {pedido_id} não encontrado")
        return f"Pedido {pedido_id} não encontrado"
    except Exception as e:
        logger.error(f"Erro ao enviar notificação do pedido {pedido_id}: {str(e)}")
        return f"Erro: {str(e)}"


# @shared_task  # Descomente quando instalar celery
def gerar_relatorio_diario():
    """Task para gerar relatório diário de vendas."""
    try:
        from datetime import date
        from django.db.models import Sum, Count
        
        hoje = date.today()
        
        # Pedidos do dia
        pedidos_hoje = Pedido.objects.filter(created_at__date=hoje)
        
        estatisticas = {
            'data': hoje.strftime('%d/%m/%Y'),
            'total_pedidos': pedidos_hoje.count(),
            'pedidos_entregues': pedidos_hoje.filter(status=StatusPedido.DELIVERED).count(),
            'receita_total': pedidos_hoje.aggregate(total=Sum('total_price'))['total'] or 0,
            'ticket_medio': 0
        }
        
        if estatisticas['total_pedidos'] > 0:
            estatisticas['ticket_medio'] = estatisticas['receita_total'] / estatisticas['total_pedidos']
        
        logger.info(f"Relatório diário gerado: {estatisticas}")
        return estatisticas
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório diário: {str(e)}")
        return f"Erro: {str(e)}"