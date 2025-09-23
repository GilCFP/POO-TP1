from django.db import models
from decimal import Decimal
from datetime import date
from enum import Enum

class Produto(models.Model):
    """
    Representa um produto vendável no restaurante.
    Esta classe é a versão Django da sua classe original 'Produto'.
    """
    name = models.CharField(max_length=100, verbose_name="Nome")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço")
    available = models.BooleanField(default=True, verbose_name="Disponível")

    def apply_discount(self, discount: float):
        """Aplica um desconto percentual ao preço do produto."""
        if 0 <= discount <= 1:
            self.price *= (Decimal('1.0') - Decimal(str(discount)))
            self.save()
        else:
            raise ValueError("O desconto deve estar entre 0 e 1.")

    def __str__(self):
        return self.name

class RestricaoAlimentar(models.Model):
    """Representa uma restrição alimentar, como 'Glúten' ou 'Lactose'."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome")

    class Meta:
        verbose_name = "Restrição Alimentar"
        verbose_name_plural = "Restrições Alimentares"

    def __str__(self):
        return self.name

class Alimento(Produto):
    """
    Representa um alimento, que é um tipo de Produto com detalhes adicionais.
    Herda de Produto usando herança multi-tabela do Django.
    """
    expiration_date = models.DateField(verbose_name="Data de Validade")
    calories = models.PositiveIntegerField(verbose_name="Calorias")
    time_to_prepare = models.PositiveIntegerField(
        default=0,
        verbose_name="Tempo de Preparo",
        help_text="Tempo em minutos"
    )
    alimentary_restrictions = models.ManyToManyField(
        RestricaoAlimentar,
        blank=True,
        verbose_name="Restrições Alimentares"
    )
    is_ingredient = models.BooleanField(
        default=False,
        verbose_name="É um ingrediente?",
        help_text="Marque se este alimento pode ser usado como ingrediente em outros."
    )
    additional_ingredients = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        verbose_name="Ingredientes Adicionais",
        limit_choices_to={'is_ingredient': True}
    )

    def is_expired(self):
        """Verifica se o alimento está vencido."""
        return date.today() > self.expiration_date
    is_expired.boolean = True
    is_expired.short_description = 'Vencido?'


class Combo(Produto):
    """
    Representa um combo, que é um Produto composto por outros Produtos.
    Herda de Produto e usa uma relação ManyToManyField para os itens.
    """
    items = models.ManyToManyField(
        Produto,
        related_name="member_of_combos",
        verbose_name="Itens do Combo"
    )

    @property
    def calculated_price(self):
        """Calcula o preço somando o valor de todos os itens."""
        if not self.pk:
            return Decimal('0.00')
        return self.items.aggregate(total=models.Sum('price'))['total'] or Decimal('0.00')

    def get_time_to_prepare(self):
        """
        Calcula o tempo total de preparo somando o tempo dos itens que são Alimentos.
        """
        total_time = 0
        for produto in self.items.select_related('alimento'):
            # hasattr verifica se o produto tem um 'alimento' relacionado (ou seja, se é um Alimento)
            if hasattr(produto, 'alimento'):
                total_time += produto.alimento.time_to_prepare
        return total_time
    get_time_to_prepare.short_description = "Tempo de Preparo (min)"


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


class Cliente(models.Model):
    """Representa um cliente do restaurante."""
    name = models.CharField(max_length=100, verbose_name="Nome")
    balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.0, 
        verbose_name="Saldo"
    )
    address = models.TextField(blank=True, null=True, verbose_name="Endereço")
    alimentary_restrictions = models.ManyToManyField(
        RestricaoAlimentar,
        blank=True,
        verbose_name="Restrições Alimentares"
    )

    def add_funds(self, amount: float):
        """Adiciona fundos ao saldo do cliente."""
        if amount > 0:
            self.balance += Decimal(str(amount))
            self.save()
        else:
            raise ValueError("O valor deve ser positivo")

    def remove_funds(self, amount: float):
        """Remove fundos do saldo do cliente."""
        if 0 < amount <= self.balance:
            self.balance -= Decimal(str(amount))
            self.save()
        else:
            raise ValueError("Fundos insuficientes ou valor inválido")

    def can_consume(self, produto):
        """Verifica se o cliente pode consumir um produto baseado em suas restrições."""
        if hasattr(produto, 'alimento'):
            cliente_restrictions = set(self.alimentary_restrictions.all())
            produto_restrictions = set(produto.alimento.alimentary_restrictions.all())
            return not cliente_restrictions.intersection(produto_restrictions)
        return True

    def __str__(self):
        return self.name


class Pedido(models.Model):
    """Representa um pedido feito por um cliente."""
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE, 
        related_name="pedidos",
        verbose_name="Cliente"
    )
    items = models.ManyToManyField(
        Produto,
        through='ItemPedido',
        verbose_name="Itens"
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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def add_item(self, produto, quantidade=1):
        """Adiciona um item ao pedido."""
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
        """Muda o status do pedido."""
        if new_status < self.status and new_status != StatusPedido.CANCELED:
            raise ValueError("Não é possível voltar para um status anterior")
        self.status = new_status
        self.save()

    def go_to_next_status(self):
        """Avança para o próximo status."""
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

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.name} - {self.get_status_display()}"


class ItemPedido(models.Model):
    """Modelo intermediário para representar itens de um pedido com quantidade."""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1, verbose_name="Quantidade")

    class Meta:
        unique_together = ('pedido', 'produto')
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"

    def __str__(self):
        return f"{self.quantidade}x {self.produto.name}"


class Bebida(Alimento):
    """Representa uma bebida, que é um tipo de Alimento com volume e indicação alcoólica."""
    volume_ml = models.PositiveIntegerField(verbose_name="Volume (ml)")
    is_alcoholic = models.BooleanField(default=False, verbose_name="É alcoólica?")

    class Meta:
        verbose_name = "Bebida"
        verbose_name_plural = "Bebidas"


class Comida(Alimento):
    """Representa uma comida, que é um tipo de Alimento com número de pessoas servidas."""
    persons_served = models.PositiveIntegerField(
        default=1,
        verbose_name="Pessoas servidas"
    )

    class Meta:
        verbose_name = "Comida"
        verbose_name_plural = "Comidas"


class Caixa(models.Model):
    """Representa o caixa do restaurante."""
    total_revenue = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.0,
        verbose_name="Receita Total"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    def process_payment(self, cliente, pedido):
        """Processa o pagamento de um pedido."""
        if cliente.balance >= pedido.total_price:
            cliente.remove_funds(float(pedido.total_price))
            self.total_revenue += pedido.total_price
            self.save()
            pedido.change_status(StatusPedido.PENDING_PAYMENT)
        else:
            raise ValueError("Fundos insuficientes para o pagamento")

    def __str__(self):
        return f"Caixa - Receita: R$ {self.total_revenue:.2f}"

    class Meta:
        verbose_name = "Caixa"
        verbose_name_plural = "Caixas"


class Cozinha(models.Model):
    """Representa a cozinha do restaurante."""
    number_of_chefs = models.PositiveIntegerField(
        default=1,
        verbose_name="Número de Chefs"
    )
    orders_in_progress = models.ManyToManyField(
        Pedido,
        blank=True,
        related_name="kitchen_in_progress",
        verbose_name="Pedidos em Progresso"
    )
    orders_in_queue = models.ManyToManyField(
        Pedido,
        blank=True,
        related_name="kitchen_queue",
        verbose_name="Pedidos na Fila"
    )

    @property
    def full_capacity(self):
        """Retorna a capacidade máxima da cozinha."""
        return self.number_of_chefs

    @property
    def current_capacity(self):
        """Retorna a capacidade atual em uso."""
        return self.orders_in_progress.count()

    def start_next_order(self):
        """Inicia o próximo pedido da fila."""
        if self.current_capacity >= self.full_capacity:
            raise ValueError("Cozinha está na capacidade máxima")
        
        queue_orders = self.orders_in_queue.filter(status=StatusPedido.PENDING_PAYMENT)
        if not queue_orders.exists():
            raise ValueError("Não há pedidos na fila")
        
        order = queue_orders.first()
        self.orders_in_queue.remove(order)
        self.orders_in_progress.add(order)
        order.go_to_next_status()

    def add_order_to_queue(self, pedido):
        """Adiciona um pedido à fila."""
        if pedido.status != StatusPedido.PENDING_PAYMENT:
            raise ValueError("Apenas pedidos com status PENDING_PAYMENT podem ser adicionados à fila")
        self.orders_in_queue.add(pedido)

    def complete_order(self, pedido):
        """Completa um pedido."""
        if pedido in self.orders_in_progress.all():
            self.orders_in_progress.remove(pedido)
            pedido.go_to_next_status()
        else:
            raise ValueError("Pedido não encontrado em progresso")

    def __str__(self):
        return f"Cozinha - {self.number_of_chefs} chefs - {self.current_capacity}/{self.full_capacity} ocupação"

    class Meta:
        verbose_name = "Cozinha"
        verbose_name_plural = "Cozinhas"


class Restaurante(models.Model):
    """Representa o restaurante."""
    name = models.CharField(max_length=100, verbose_name="Nome")
    menu = models.ManyToManyField(
        Produto,
        blank=True,
        related_name="restaurants",
        verbose_name="Menu"
    )
    clients = models.ManyToManyField(
        Cliente,
        blank=True,
        related_name="restaurants",
        verbose_name="Clientes"
    )
    cash_register = models.OneToOneField(
        Caixa,
        on_delete=models.CASCADE,
        verbose_name="Caixa"
    )
    kitchen = models.OneToOneField(
        Cozinha,
        on_delete=models.CASCADE,
        verbose_name="Cozinha"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    def add_product_to_menu(self, produto):
        """Adiciona um produto ao menu."""
        self.menu.add(produto)

    def register_client(self, cliente):
        """Registra um cliente."""
        self.clients.add(cliente)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Restaurante"
        verbose_name_plural = "Restaurantes"