from django.db import models
from decimal import Decimal
from apps.core.models import TimeStampedModel


class StatusPedido(models.TextChoices):
    """Representa os diferentes status que um pedido pode ter."""
    CANCELED = '-1', 'Cancelado'
    ORDERING = '0', 'Fazendo pedido'
    PENDING_PAYMENT = '1', 'Aguardando pagamento'
    WAITING = '2', 'Aguardando'
    PREPARING = '3', 'Preparando'
    READY = '4', 'Pronto'
    BEING_DELIVERED = '5', 'Sendo entregue'
    DELIVERED = '6', 'Entregue'


class Pedido(TimeStampedModel):
    """Representa um pedido feito por um cliente."""
    cliente = models.ForeignKey(
        'cliente.Cliente', 
        on_delete=models.CASCADE, 
        related_name="pedidos",
        verbose_name="Cliente"
    )
    items = models.ManyToManyField(
        'produto.Produto',
        through='ItemPedido',
        verbose_name="Itens",
        related_name="pedidos"
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.0,
        verbose_name="Preço Total"
    )
    status = models.CharField(
        max_length=2,
        choices=StatusPedido.choices,
        default=StatusPedido.ORDERING,
        verbose_name="Status"
    )
    delivery_address = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Endereço de Entrega"
    )
    estimated_delivery_time = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Tempo Estimado de Entrega"
    )
    notes = models.TextField(
        blank=True, 
        verbose_name="Observações"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('saldo', 'Saldo da Conta'),
            ('cartao', 'Cartão'),
            ('dinheiro', 'Dinheiro'),
            ('pix', 'PIX'),
        ],
        default='saldo',
        verbose_name="Método de Pagamento"
    )

    def add_item(self, produto, quantidade=1):
        """Adiciona um item ao pedido."""
        if self.status != StatusPedido.ORDERING:
            raise ValueError("Não é possível modificar um pedido que não está sendo montado")
            
        item, created = ItemPedido.objects.get_or_create(
            pedido=self,
            produto=produto,
            defaults={'quantidade': quantidade}
        )
        if not created:
            item.quantidade += quantidade
            item.save()
        self.calculate_total()

    def remove_item(self, produto):
        """Remove um item do pedido."""
        if self.status != StatusPedido.ORDERING:
            raise ValueError("Não é possível modificar um pedido que não está sendo montado")
            
        try:
            item = ItemPedido.objects.get(pedido=self, produto=produto)
            item.delete()
            self.calculate_total()
        except ItemPedido.DoesNotExist:
            raise ValueError("Item não encontrado no pedido")

    def calculate_total(self):
        """Calcula o total do pedido."""
        total = sum(
            item.produto.price * item.quantidade 
            for item in self.itempedido_set.all()
        )
        self.total_price = total
        self.save()

    def change_status(self, new_status):
        """Muda o status do pedido com validações."""
        if new_status < self.status and new_status != StatusPedido.CANCELED:
            raise ValueError("Não é possível voltar para um status anterior")
        
        # Validações específicas por status
        if new_status == StatusPedido.PENDING_PAYMENT and not self.items.exists():
            raise ValueError("Não é possível finalizar um pedido sem itens")
            
        self.status = new_status
        self.save()

        # Trigger para notificações (pode ser implementado com signals)
        self._notify_status_change()

    def go_to_next_status(self):
        """Avança para o próximo status automaticamente."""
        if self.status == StatusPedido.CANCELED:
            raise ValueError("Não é possível mudar o status de um pedido cancelado")
        elif self.status == StatusPedido.DELIVERED:
            raise ValueError("Pedido já foi entregue")
        else:
            status_values = [choice[0] for choice in StatusPedido.choices]
            current_index = status_values.index(self.status)
            if current_index < len(status_values) - 1:
                self.status = status_values[current_index + 1]
                self.save()
                self._notify_status_change()

    def _notify_status_change(self):
        """Método interno para notificar mudanças de status."""
        # Implementar notificações via WebSocket, email, etc.
        pass

    def get_estimated_prep_time(self):
        """Calcula tempo estimado de preparo baseado nos itens."""
        total_time = 0
        for item in self.itempedido_set.select_related('produto'):
            produto = item.produto
            # Verifica se o produto é um alimento com tempo de preparo
            if hasattr(produto, 'alimento'):
                total_time += produto.alimento.time_to_prepare * item.quantidade
            elif hasattr(produto, 'combo'):
                total_time += produto.combo.get_time_to_prepare() * item.quantidade
        
        # Adiciona tempo base e fator de segurança
        return total_time + 5  # 5 minutos de margem

    def get_total_calories(self):
        """Calcula total de calorias do pedido."""
        total_calories = 0
        for item in self.itempedido_set.select_related('produto'):
            produto = item.produto
            if hasattr(produto, 'alimento'):
                total_calories += produto.alimento.calories * item.quantidade
            elif hasattr(produto, 'combo'):
                total_calories += produto.combo.get_total_calories() * item.quantidade
        return total_calories

    def can_be_canceled(self):
        """Verifica se o pedido pode ser cancelado."""
        non_cancelable_statuses = [
            StatusPedido.BEING_DELIVERED, 
            StatusPedido.DELIVERED, 
            StatusPedido.CANCELED
        ]
        return self.status not in non_cancelable_statuses

    def get_items_summary(self):
        """Retorna resumo dos itens do pedido."""
        items = []
        for item in self.itempedido_set.select_related('produto'):
            items.append({
                'produto': item.produto.name,
                'quantidade': item.quantidade,
                'preco_unitario': item.produto.price,
                'subtotal': item.produto.price * item.quantidade
            })
        return items

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.name} - {self.get_status_display()}"

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-created_at']


class ItemPedido(TimeStampedModel):
    """Modelo intermediário para representar itens de um pedido com quantidade."""
    pedido = models.ForeignKey(
        Pedido, 
        on_delete=models.CASCADE,
        verbose_name="Pedido"
    )
    produto = models.ForeignKey(
        'produto.Produto', 
        on_delete=models.CASCADE,
        related_name='pedido_items',
        verbose_name="Produto"
    )
    quantidade = models.PositiveIntegerField(
        default=1, 
        verbose_name="Quantidade"
    )
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Preço Unitário",
        help_text="Preço do produto no momento do pedido"
    )
    special_instructions = models.TextField(
        blank=True,
        verbose_name="Instruções Especiais",
        help_text="Ex: sem cebola, ponto da carne, etc."
    )

    def save(self, *args, **kwargs):
        """Salva o preço unitário do produto no momento do pedido."""
        if not self.unit_price:
            self.unit_price = self.produto.price
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        """Calcula o subtotal do item."""
        return self.unit_price * self.quantidade

    def get_nutrition_info(self):
        """Retorna informações nutricionais do item."""
        if hasattr(self.produto, 'alimento'):
            alimento = self.produto.alimento
            return {
                'calories_per_unit': alimento.calories,
                'total_calories': alimento.calories * self.quantidade,
                'restrictions': list(alimento.alimentary_restrictions.values_list('name', flat=True))
            }
        return None

    class Meta:
        unique_together = ('pedido', 'produto')
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.quantidade}x {self.produto.name} - R$ {self.subtotal:.2f}"


class HistoricoPedido(TimeStampedModel):
    """Histórico de mudanças de status dos pedidos para auditoria."""
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="historico",
        verbose_name="Pedido"
    )
    status_anterior = models.CharField(
        max_length=2,
        choices=StatusPedido.choices,
        verbose_name="Status Anterior"
    )
    status_novo = models.CharField(
        max_length=2,
        choices=StatusPedido.choices,
        verbose_name="Status Novo"
    )
    usuario = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Usuário",
        help_text="Usuário que fez a alteração"
    )
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações"
    )

    class Meta:
        verbose_name = "Histórico do Pedido"
        verbose_name_plural = "Histórico dos Pedidos"
        ordering = ['-created_at']

    def __str__(self):
        return f"Pedido #{self.pedido.id}: {self.get_status_anterior_display()} → {self.get_status_novo_display()}"
