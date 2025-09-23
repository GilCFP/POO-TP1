"""
Utilitários e validadores para o sistema de restaurante.
"""
from datetime import date, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError


class RestauranteValidators:
    """Validadores específicos do domínio do restaurante."""
    
    @staticmethod
    def validate_price(price):
        """Valida se o preço é válido."""
        if price <= 0:
            raise ValidationError("O preço deve ser maior que zero")
        
        if price > Decimal('9999.99'):
            raise ValidationError("O preço não pode exceder R$ 9.999,99")
    
    @staticmethod
    def validate_discount(discount):
        """Valida se o desconto é válido."""
        if not 0 <= discount <= 1:
            raise ValidationError("O desconto deve estar entre 0% e 100%")
    
    @staticmethod
    def validate_expiration_date(expiration_date):
        """Valida se a data de validade é válida."""
        if expiration_date < date.today():
            raise ValidationError("A data de validade não pode ser no passado")
    
    @staticmethod
    def validate_balance(balance):
        """Valida se o saldo é válido."""
        if balance < 0:
            raise ValidationError("O saldo não pode ser negativo")


class RestauranteUtils:
    """Utilitários gerais para o sistema."""
    
    @staticmethod
    def calculate_combo_discount(items_total, combo_discount_percentage=0.1):
        """Calcula desconto padrão para combos."""
        return items_total * Decimal(str(combo_discount_percentage))
    
    @staticmethod
    def format_currency(value):
        """Formata um valor como moeda brasileira."""
        return f"R$ {value:.2f}".replace('.', ',')
    
    @staticmethod
    def calculate_delivery_time(distance_km):
        """Calcula tempo estimado de entrega baseado na distância."""
        base_time = 30  # 30 minutos base
        additional_time = max(0, (distance_km - 5) * 5)  # 5 min a mais por km após 5km
        return base_time + additional_time
    
    @staticmethod
    def get_business_hours():
        """Retorna horário de funcionamento do restaurante."""
        return {
            'abertura': '08:00',
            'fechamento': '22:00',
            'dias_funcionamento': ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado']
        }
    
    @staticmethod
    def is_business_hours(current_time=None):
        """Verifica se está no horário de funcionamento."""
        # Implementação simplificada - em produção seria mais complexa
        if current_time is None:
            from datetime import datetime
            current_time = datetime.now().time()
        
        return current_time.hour >= 8 and current_time.hour < 22
    
    @staticmethod
    def calculate_preparation_time(pedido):
        """Calcula tempo total de preparo de um pedido."""
        total_time = 0
        
        for item in pedido.itempedido_set.all():
            produto = item.produto
            
            # Se é um alimento, soma o tempo de preparo
            if hasattr(produto, 'alimento'):
                total_time += produto.alimento.time_to_prepare * item.quantidade
            
            # Se é um combo, calcula o tempo dos itens
            elif hasattr(produto, 'combo'):
                combo_time = produto.combo.get_time_to_prepare()
                total_time += combo_time * item.quantidade
        
        # Adiciona tempo base de 5 minutos
        return total_time + 5
    
    @staticmethod
    def generate_order_summary(pedido):
        """Gera resumo detalhado de um pedido."""
        summary = {
            'pedido_id': pedido.id,
            'cliente': pedido.cliente.name,
            'status': pedido.get_status_display(),
            'itens': [],
            'total': pedido.total_price,
            'tempo_preparo_estimado': RestauranteUtils.calculate_preparation_time(pedido)
        }
        
        for item in pedido.itempedido_set.all():
            item_info = {
                'produto': item.produto.name,
                'quantidade': item.quantidade,
                'preco_unitario': item.produto.price,
                'subtotal': item.produto.price * item.quantidade
            }
            
            # Adiciona informações específicas se for alimento
            if hasattr(item.produto, 'alimento'):
                alimento = item.produto.alimento
                item_info.update({
                    'calories': alimento.calories,
                    'tempo_preparo': alimento.time_to_prepare,
                    'restricoes': [r.name for r in alimento.alimentary_restrictions.all()]
                })
            
            summary['itens'].append(item_info)
        
        return summary


class StatusManager:
    """Gerenciador de status e transições."""
    
    @staticmethod
    def get_next_status(current_status):
        """Retorna o próximo status válido."""
        from ..models import StatusPedido
        
        status_flow = [
            StatusPedido.ORDERING,
            StatusPedido.PENDING_PAYMENT,
            StatusPedido.WAITING,
            StatusPedido.PREPARING,
            StatusPedido.READY,
            StatusPedido.BEING_DELIVERED,
            StatusPedido.DELIVERED
        ]
        
        try:
            current_index = status_flow.index(current_status)
            if current_index < len(status_flow) - 1:
                return status_flow[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    @staticmethod
    def can_transition_to(current_status, new_status):
        """Verifica se é possível transicionar entre status."""
        from ..models import StatusPedido
        
        # Sempre pode cancelar (exceto se já entregue)
        if new_status == StatusPedido.CANCELED:
            return current_status != StatusPedido.DELIVERED
        
        # Não pode voltar de cancelado
        if current_status == StatusPedido.CANCELED:
            return False
        
        # Não pode voltar no fluxo (exceto para cancelar)
        valid_transitions = {
            StatusPedido.ORDERING: [StatusPedido.PENDING_PAYMENT],
            StatusPedido.PENDING_PAYMENT: [StatusPedido.WAITING],
            StatusPedido.WAITING: [StatusPedido.PREPARING],
            StatusPedido.PREPARING: [StatusPedido.READY],
            StatusPedido.READY: [StatusPedido.BEING_DELIVERED],
            StatusPedido.BEING_DELIVERED: [StatusPedido.DELIVERED],
            StatusPedido.DELIVERED: []
        }
        
        return new_status in valid_transitions.get(current_status, [])