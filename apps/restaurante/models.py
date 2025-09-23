from django.db import models
from decimal import Decimal
from apps.core.models import TimeStampedModel
from apps.pedido.models import StatusPedido


class Restaurante(TimeStampedModel):
    """Representa o restaurante principal."""
    name = models.CharField(max_length=100, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")
    address = models.TextField(verbose_name="Endereço")
    phone = models.CharField(max_length=20, verbose_name="Telefone")
    email = models.EmailField(verbose_name="Email")
    
    # Configurações operacionais
    is_open = models.BooleanField(default=True, verbose_name="Aberto")
    opening_time = models.TimeField(verbose_name="Horário de Abertura")
    closing_time = models.TimeField(verbose_name="Horário de Fechamento")
    delivery_fee = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0.0,
        verbose_name="Taxa de Entrega"
    )
    minimum_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        verbose_name="Valor Mínimo do Pedido"
    )
    
    # Relacionamentos
    menu = models.ManyToManyField(
        'produto.Produto',
        blank=True,
        related_name="restaurants",
        verbose_name="Menu"
    )
    clients = models.ManyToManyField(
        'cliente.Cliente',
        blank=True,
        related_name="restaurants",
        verbose_name="Clientes"
    )

    def add_product_to_menu(self, produto):
        """Adiciona um produto ao menu."""
        if produto.available:
            self.menu.add(produto)
        else:
            raise ValueError("Não é possível adicionar produto indisponível ao menu")

    def remove_product_from_menu(self, produto):
        """Remove um produto do menu."""
        self.menu.remove(produto)

    def register_client(self, cliente):
        """Registra um cliente no restaurante."""
        if cliente.is_active:
            self.clients.add(cliente)
        else:
            raise ValueError("Não é possível registrar cliente inativo")

    def is_within_business_hours(self):
        """Verifica se está no horário de funcionamento."""
        from datetime import datetime
        now = datetime.now().time()
        return self.opening_time <= now <= self.closing_time

    def get_menu_by_category(self):
        """Retorna o menu organizado por categoria."""
        menu_categories = {}
        for produto in self.menu.filter(available=True):
            category = produto.category or 'Outros'
            if category not in menu_categories:
                menu_categories[category] = []
            menu_categories[category].append(produto)
        return menu_categories

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Restaurante"
        verbose_name_plural = "Restaurantes"


class Caixa(TimeStampedModel):
    """Representa o sistema de caixa do restaurante."""
    restaurante = models.OneToOneField(
        Restaurante,
        on_delete=models.CASCADE,
        related_name="caixa",
        verbose_name="Restaurante"
    )
    total_revenue = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.0,
        verbose_name="Receita Total"
    )
    daily_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        verbose_name="Receita do Dia"
    )
    last_reset_date = models.DateField(
        auto_now_add=True,
        verbose_name="Último Reset"
    )
    is_active = models.BooleanField(default=True, verbose_name="Ativo")

    def process_payment(self, cliente, pedido):
        """Processa o pagamento de um pedido."""
        from apps.pedido.models import StatusPedido
        
        if pedido.status != StatusPedido.ORDERING:
            raise ValueError("Pedido não está disponível para pagamento")
            
        if not cliente.has_sufficient_balance(pedido.total_price):
            raise ValueError("Saldo insuficiente")
        
        # Processar pagamento
        cliente.remove_funds(float(pedido.total_price))
        self.add_revenue(pedido.total_price)
        
        # Atualizar status do pedido
        pedido.change_status(StatusPedido.PENDING_PAYMENT)
        
        return True

    def add_revenue(self, amount):
        """Adiciona receita ao caixa."""
        if amount > 0:
            self.total_revenue += Decimal(str(amount))
            self.daily_revenue += Decimal(str(amount))
            self.save()

    def reset_daily_revenue(self):
        """Reseta a receita diária (função para fechamento do dia)."""
        from datetime import date
        self.daily_revenue = Decimal('0.00')
        self.last_reset_date = date.today()
        self.save()

    def get_revenue_info(self):
        """Retorna informações consolidadas de receita."""
        return {
            'total': float(self.total_revenue),
            'today': float(self.daily_revenue),
            'formatted_total': f"R$ {self.total_revenue:.2f}",
            'formatted_today': f"R$ {self.daily_revenue:.2f}"
        }

    def __str__(self):
        return f"Caixa {self.restaurante.name} - R$ {self.total_revenue:.2f}"

    class Meta:
        verbose_name = "Caixa"
        verbose_name_plural = "Caixas"


class Cozinha(TimeStampedModel):
    """Representa a cozinha do restaurante."""
    restaurante = models.OneToOneField(
        Restaurante,
        on_delete=models.CASCADE,
        related_name="cozinha",
        verbose_name="Restaurante"
    )
    number_of_chefs = models.PositiveIntegerField(
        default=1,
        verbose_name="Número de Chefs"
    )
    number_of_stations = models.PositiveIntegerField(
        default=1,
        verbose_name="Número de Estações",
        help_text="Quantas estações de preparo estão disponíveis"
    )
    is_active = models.BooleanField(default=True, verbose_name="Ativa")
    
    # Relacionamentos com pedidos (para Kanban)
    orders_in_queue = models.ManyToManyField(
        'pedido.Pedido',
        blank=True,
        related_name="kitchen_queue",
        verbose_name="Pedidos na Fila",
        limit_choices_to={'status': StatusPedido.WAITING}
    )
    orders_in_progress = models.ManyToManyField(
        'pedido.Pedido',
        blank=True,
        related_name="kitchen_in_progress",
        verbose_name="Pedidos em Progresso",
        limit_choices_to={'status': StatusPedido.PREPARING}
    )
    orders_ready = models.ManyToManyField(
        'pedido.Pedido',
        blank=True,
        related_name="kitchen_ready",
        verbose_name="Pedidos Prontos",
        limit_choices_to={'status': StatusPedido.READY}
    )

    @property
    def full_capacity(self):
        """Retorna a capacidade máxima de pedidos simultâneos."""
        return self.number_of_chefs * self.number_of_stations

    @property
    def current_capacity_usage(self):
        """Retorna a capacidade atual em uso."""
        return self.orders_in_progress.count()

    @property
    def available_capacity(self):
        """Retorna quantos pedidos ainda podem ser iniciados."""
        return self.full_capacity - self.current_capacity_usage

    def can_start_new_order(self):
        """Verifica se pode iniciar um novo pedido."""
        return self.current_capacity_usage < self.full_capacity and self.is_active

    def add_order_to_queue(self, pedido):
        """Adiciona um pedido à fila da cozinha."""
        if pedido.status != StatusPedido.PENDING_PAYMENT:
            raise ValueError("Apenas pedidos pagos podem ser adicionados à fila")
        
        # Mover pedido para status WAITING e adicionar à fila
        pedido.change_status(StatusPedido.WAITING)
        self.orders_in_queue.add(pedido)

    def start_next_order(self):
        """Inicia o preparo do próximo pedido da fila."""
        if not self.can_start_new_order():
            raise ValueError("Cozinha está na capacidade máxima ou inativa")
        
        # Pegar próximo pedido da fila (FIFO)
        next_order = self.orders_in_queue.first()
        if not next_order:
            raise ValueError("Não há pedidos na fila")
        
        # Mover da fila para em progresso
        self.orders_in_queue.remove(next_order)
        next_order.change_status(StatusPedido.PREPARING)
        self.orders_in_progress.add(next_order)
        
        return next_order

    def complete_order(self, pedido):
        """Marca um pedido como pronto."""
        if pedido not in self.orders_in_progress.all():
            raise ValueError("Pedido não está em progresso nesta cozinha")
        
        # Mover de em progresso para pronto
        self.orders_in_progress.remove(pedido)
        pedido.change_status(StatusPedido.READY)
        self.orders_ready.add(pedido)
        
        return pedido

    def deliver_order(self, pedido):
        """Marca um pedido como saindo para entrega."""
        if pedido not in self.orders_ready.all():
            raise ValueError("Pedido não está pronto para entrega")
        
        # Remover dos prontos e marcar como sendo entregue
        self.orders_ready.remove(pedido)
        pedido.change_status(StatusPedido.BEING_DELIVERED)
        
        return pedido

    def get_queue_status(self):
        """Retorna status completo da fila de pedidos."""
        return {
            'queue_count': self.orders_in_queue.count(),
            'in_progress_count': self.orders_in_progress.count(),
            'ready_count': self.orders_ready.count(),
            'capacity_usage': self.current_capacity_usage,
            'available_capacity': self.available_capacity,
            'is_at_capacity': not self.can_start_new_order()
        }

    def get_estimated_wait_time(self):
        """Calcula tempo estimado de espera para novos pedidos."""
        queue_count = self.orders_in_queue.count()
        avg_prep_time = 15  # minutos por pedido (pode ser calculado dinamicamente)
        
        if self.can_start_new_order():
            return avg_prep_time
        else:
            # Estimar baseado na fila e capacidade
            return (queue_count // self.full_capacity + 1) * avg_prep_time

    def __str__(self):
        return f"Cozinha {self.restaurante.name} - {self.current_capacity_usage}/{self.full_capacity}"

    class Meta:
        verbose_name = "Cozinha"
        verbose_name_plural = "Cozinhas"


class EstacaoTrabalho(TimeStampedModel):
    """Representa uma estação de trabalho individual na cozinha."""
    cozinha = models.ForeignKey(
        Cozinha,
        on_delete=models.CASCADE,
        related_name="estacoes",
        verbose_name="Cozinha"
    )
    name = models.CharField(max_length=50, verbose_name="Nome da Estação")
    tipo = models.CharField(
        max_length=30,
        choices=[
            ('grill', 'Grill'),
            ('fryer', 'Fritadeira'),
            ('prep', 'Preparo'),
            ('drinks', 'Bebidas'),
            ('dessert', 'Sobremesas'),
            ('assembly', 'Montagem'),
        ],
        verbose_name="Tipo"
    )
    is_active = models.BooleanField(default=True, verbose_name="Ativa")
    current_order = models.ForeignKey(
        'pedido.Pedido',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Pedido Atual"
    )

    def assign_order(self, pedido):
        """Atribui um pedido a esta estação."""
        if self.current_order:
            raise ValueError("Estação já está ocupada")
        
        self.current_order = pedido
        self.save()

    def complete_current_order(self):
        """Completa o pedido atual da estação."""
        if not self.current_order:
            raise ValueError("Nenhum pedido em andamento nesta estação")
        
        completed_order = self.current_order
        self.current_order = None
        self.save()
        
        return completed_order

    @property
    def is_available(self):
        """Verifica se a estação está disponível."""
        return self.is_active and not self.current_order

    def __str__(self):
        status = "Livre" if self.is_available else f"Ocupada (Pedido #{self.current_order.id})"
        return f"{self.name} - {status}"

    class Meta:
        verbose_name = "Estação de Trabalho"
        verbose_name_plural = "Estações de Trabalho"
        unique_together = ('cozinha', 'name')
