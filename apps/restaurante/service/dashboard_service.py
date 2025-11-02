from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Union
from decimal import Decimal

from django.db.models import (
    Sum, Count, Avg, F, Q,
    DateTimeField, DurationField
)
from django.db.models.functions import TruncHour, Extract
from django.utils import timezone

from apps.pedido.models import Pedido, ItemPedido, StatusPedido
from apps.produto.models import Produto
from apps.restaurante.models import Restaurante, Cozinha


class DashboardService:
    """
    Serviço para agregação de dados do dashboard de vendas e operações do restaurante.
    """
    
    def __init__(self, start_date: date, end_date: date, restaurante_id: int):
        """
        Inicializa o serviço com período e restaurante específicos.
        
        Args:
            start_date: Data inicial do período
            end_date: Data final do período (inclusiva)
            restaurante_id: ID do restaurante para filtrar dados
        """
        self.start_date = start_date
        self.end_date = end_date
        self.restaurante_id = restaurante_id
        
        # Base queryset para pedidos entregues no período
        self.base_queryset = Pedido.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status=StatusPedido.DELIVERED
            # TODO: Adicionar filtro por restaurante quando FK estiver definida
            # restaurante_id=restaurante_id
        )
    
    def get_sales_metrics(self) -> Dict[str, Union[Decimal, int, float]]:
        """
        Calcula métricas básicas de vendas.
        
        Returns:
            Dict contendo total_sales, total_orders e average_ticket
        """
        metrics = self.base_queryset.aggregate(
            total_sales=Sum('total_price'),
            total_orders=Count('id')
        )
        
        total_sales = metrics['total_sales'] or Decimal('0.00')
        total_orders = metrics['total_orders'] or 0
        
        # Calcular ticket médio
        average_ticket = float(total_sales / total_orders) if total_orders > 0 else 0.0
        
        return {
            'total_sales': total_sales,
            'total_orders': total_orders,
            'average_ticket': round(average_ticket, 2)
        }
    
    def get_average_order_time(self) -> float:
        """
        Placeholder para tempo médio de preparo dos pedidos.
        
        Returns:
            Tempo médio de preparo em minutos (placeholder: 0.0)
        """
        # TODO: Implementar quando campos de tempo de preparo forem adicionados aos models
        # Os campos data_inicio_preparo e data_pronto não existem no modelo atual
        return 0.0
    
    def get_returned_orders_metrics(self) -> Dict[str, Union[int, Decimal]]:
        """
        Calcula métricas de pedidos cancelados/devolvidos.
        
        Returns:
            Dict contendo count e valor total dos pedidos cancelados
        """
        cancelled_orders = Pedido.objects.filter(
            created_at__date__gte=self.start_date,
            created_at__date__lte=self.end_date,
            status=StatusPedido.CANCELED
            # TODO: Adicionar filtro por restaurante
        )
        
        metrics = cancelled_orders.aggregate(
            returned_orders_count=Count('id'),
            returned_orders_value=Sum('total_price')
        )
        
        return {
            'returned_orders_count': metrics['returned_orders_count'] or 0,
            'returned_orders_value': metrics['returned_orders_value'] or Decimal('0.00')
        }
    
    def get_sales_by_hour(self) -> List[Dict[str, int]]:
        """
        Agrupa vendas por hora para gráfico de barras.
        
        Returns:
            Lista com vendas por hora (0-23), garantindo todas as horas
        """
        # Agrupar pedidos por hora
        hourly_sales = self.base_queryset.annotate(
            hour=TruncHour('created_at')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')
        
        # Criar dicionário com os dados existentes
        sales_by_hour_dict = {}
        for sale in hourly_sales:
            hour = sale['hour'].hour if sale['hour'] else 0
            sales_by_hour_dict[hour] = sale['count']
        
        # Garantir que todas as 24 horas estejam presentes
        result = []
        for hour in range(24):
            result.append({
                'hour': hour,
                'count': sales_by_hour_dict.get(hour, 0)
            })
        
        return result
    
    def get_top_selling_products(self, limit: int = 5) -> List[Dict[str, Union[str, int]]]:
        """
        Retorna os produtos mais vendidos baseado na quantidade.
        
        Args:
            limit: Número máximo de produtos a retornar
            
        Returns:
            Lista dos produtos mais vendidos
        """
        # Filtrar itens de pedidos entregues
        completed_order_items = ItemPedido.objects.filter(
            pedido__created_at__date__gte=self.start_date,
            pedido__created_at__date__lte=self.end_date,
            pedido__status=StatusPedido.DELIVERED
            # TODO: Adicionar filtro por restaurante via pedido
        )
        
        # Agrupar por produto e somar quantidades
        top_products = completed_order_items.values(
            'produto__name'
        ).annotate(
            total_sold=Sum('quantidade')
        ).order_by('-total_sold')[:limit]
        
        return [
            {
                'produto_nome': item['produto__name'],
                'total_sold': item['total_sold']
            }
            for item in top_products
        ]
    
    def get_kitchen_capacity_metrics(self) -> Dict[str, int]:
        """
        Busca métricas de capacidade da cozinha do restaurante.
        
        Returns:
            Dict contendo capacidade total e número de chefs
        """
        try:
            cozinha = Cozinha.objects.get(restaurante_id=self.restaurante_id)
            return {
                'full_capacity': cozinha.full_capacity,
                'number_of_chefs': cozinha.number_of_chefs
            }
        except Cozinha.DoesNotExist:
            return {
                'full_capacity': 0,
                'number_of_chefs': 0
            }
    
    def get_expenses_metrics(self) -> Dict[str, Union[int, bool]]:
        """
        Placeholder para métricas de despesas.
        
        TODO: Implementar quando model Despesa estiver disponível
        
        Returns:
            Dict placeholder para despesas
        """
        # TODO: Implementar quando model Despesa for criado
        return {
            'total_expenses': 0,
            'placeholder': True
        }
    
    def get_employee_metrics(self) -> Dict[str, Union[int, bool]]:
        """
        Placeholder para métricas de funcionários.
        
        TODO: Implementar quando model Funcionario estiver disponível
        
        Returns:
            Dict placeholder para funcionários
        """
        # TODO: Implementar quando model Funcionario for criado
        return {
            'active_employees': 0,
            'placeholder': True
        }
    
    def get_all_dashboard_data(self) -> Dict[str, Union[Dict, List, float]]:
        """
        Método mestre que compila todos os dados do dashboard.
        
        Returns:
            Dict completo com todas as métricas do dashboard
        """
        return {
            'period': {
                'start_date': self.start_date.isoformat(),
                'end_date': self.end_date.isoformat(),
                'restaurante_id': self.restaurante_id
            },
            'sales_metrics': self.get_sales_metrics(),
            'avg_order_time': self.get_average_order_time(),
            'returned_orders_metrics': self.get_returned_orders_metrics(),
            'sales_by_hour': self.get_sales_by_hour(),
            'top_selling_products': self.get_top_selling_products(),
            'kitchen_capacity_metrics': self.get_kitchen_capacity_metrics(),
            'expenses_metrics': self.get_expenses_metrics(),
            'employee_metrics': self.get_employee_metrics()
        }