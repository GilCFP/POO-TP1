from django.db import models
from decimal import Decimal
from datetime import date
from apps.core.models import TimeStampedModel


class RestricaoAlimentar(TimeStampedModel):
    """Representa uma restrição alimentar, como 'Glúten' ou 'Lactose'."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Ícone")

    class Meta:
        verbose_name = "Restrição Alimentar"
        verbose_name_plural = "Restrições Alimentares"
        ordering = ['name']

    def __str__(self):
        return self.name


class Produto(TimeStampedModel):
    """
    Representa um produto vendável no restaurante.
    Classe base para todos os produtos.
    """
    name = models.CharField(max_length=100, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço")
    available = models.BooleanField(default=True, verbose_name="Disponível")
    image = models.ImageField(upload_to='produtos/', blank=True, null=True, verbose_name="Imagem")
    category = models.CharField(max_length=50, blank=True, verbose_name="Categoria")
    
    def apply_discount(self, discount: float):
        """Aplica um desconto percentual ao preço do produto."""
        if 0 <= discount <= 1:
            self.price *= (Decimal('1.0') - Decimal(str(discount)))
            self.save()
        else:
            raise ValueError("O desconto deve estar entre 0 e 1.")

    def get_formatted_price(self):
        """Retorna o preço formatado em reais."""
        return f"R$ {self.price:.2f}"

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Alimento(Produto):
    """
    Representa um alimento, que é um tipo de Produto com detalhes nutricionais.
    """
    expiration_date = models.DateField(verbose_name="Data de Validade")
    calories = models.PositiveIntegerField(verbose_name="Calorias")
    time_to_prepare = models.PositiveIntegerField(
        default=0,
        verbose_name="Tempo de Preparo",
        help_text="Tempo em minutos"
    )
    weight_grams = models.PositiveIntegerField(
        default=0, 
        verbose_name="Peso (gramas)"
    )
    alimentary_restrictions = models.ManyToManyField(
        RestricaoAlimentar,
        blank=True,
        verbose_name="Restrições Alimentares",
        related_name="alimentos"
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
        limit_choices_to={'is_ingredient': True},
        related_name="used_in_foods"
    )

    def is_expired(self):
        """Verifica se o alimento está vencido."""
        return date.today() > self.expiration_date
    is_expired.boolean = True
    is_expired.short_description = 'Vencido?'

    def days_until_expiration(self):
        """Retorna quantos dias faltam para o vencimento."""
        delta = self.expiration_date - date.today()
        return delta.days

    def get_nutrition_info(self):
        """Retorna informações nutricionais formatadas."""
        return {
            'calories': self.calories,
            'weight': f"{self.weight_grams}g",
            'restrictions': list(self.alimentary_restrictions.values_list('name', flat=True))
        }

    class Meta:
        verbose_name = "Alimento"
        verbose_name_plural = "Alimentos"


class Bebida(Alimento):
    """Representa uma bebida, que é um tipo de Alimento com volume e indicação alcoólica."""
    volume_ml = models.PositiveIntegerField(verbose_name="Volume (ml)")
    is_alcoholic = models.BooleanField(default=False, verbose_name="É alcoólica?")
    temperature = models.CharField(
        max_length=20,
        choices=[
            ('gelada', 'Gelada'),
            ('natural', 'Natural'),
            ('quente', 'Quente'),
        ],
        default='natural',
        verbose_name="Temperatura"
    )

    def get_volume_info(self):
        """Retorna informações de volume formatadas."""
        if self.volume_ml >= 1000:
            return f"{self.volume_ml/1000:.1f}L"
        return f"{self.volume_ml}ml"

    class Meta:
        verbose_name = "Bebida"
        verbose_name_plural = "Bebidas"


class Comida(Alimento):
    """Representa uma comida, que é um tipo de Alimento com número de pessoas servidas."""
    persons_served = models.PositiveIntegerField(
        default=1,
        verbose_name="Pessoas servidas"
    )
    spice_level = models.CharField(
        max_length=20,
        choices=[
            ('suave', 'Suave'),
            ('medio', 'Médio'),
            ('picante', 'Picante'),
            ('muito_picante', 'Muito Picante'),
        ],
        default='suave',
        verbose_name="Nível de Pimenta"
    )

    def get_serving_info(self):
        """Retorna informações de porção."""
        return f"Serve {self.persons_served} pessoa{'s' if self.persons_served > 1 else ''}"

    class Meta:
        verbose_name = "Comida"
        verbose_name_plural = "Comidas"


class Combo(Produto):
    """
    Representa um combo, que é um Produto composto por outros Produtos.
    """
    items = models.ManyToManyField(
        Produto,
        through='ComboItem',
        related_name="member_of_combos",
        verbose_name="Itens do Combo"
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.10,
        verbose_name="Desconto (%)",
        help_text="Desconto aplicado sobre o valor total dos itens"
    )

    @property
    def calculated_price_without_discount(self):
        """Calcula o preço somando o valor de todos os itens sem desconto."""
        if not self.pk:
            return Decimal('0.00')
        
        total = Decimal('0.00')
        for combo_item in self.comboitem_set.all():
            total += combo_item.produto.price * combo_item.quantity
        return total

    @property
    def calculated_discount_amount(self):
        """Calcula o valor do desconto."""
        base_price = self.calculated_price_without_discount
        return base_price * (self.discount_percentage / 100)

    @property
    def calculated_final_price(self):
        """Calcula o preço final com desconto."""
        return self.calculated_price_without_discount - self.calculated_discount_amount

    def get_time_to_prepare(self):
        """
        Calcula o tempo total de preparo somando o tempo dos itens que são Alimentos.
        """
        total_time = 0
        for combo_item in self.comboitem_set.select_related('produto'):
            produto = combo_item.produto
            if hasattr(produto, 'alimento'):
                total_time += produto.alimento.time_to_prepare * combo_item.quantity
        return total_time
    get_time_to_prepare.short_description = "Tempo de Preparo (min)"

    def get_total_calories(self):
        """Calcula o total de calorias do combo."""
        total_calories = 0
        for combo_item in self.comboitem_set.select_related('produto'):
            produto = combo_item.produto
            if hasattr(produto, 'alimento'):
                total_calories += produto.alimento.calories * combo_item.quantity
        return total_calories

    class Meta:
        verbose_name = "Combo"
        verbose_name_plural = "Combos"


class ComboItem(TimeStampedModel):
    """Modelo intermediário para representar itens de um combo com quantidade."""
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE, related_name='combo_items')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='combo_memberships')
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantidade")

    class Meta:
        unique_together = ('combo', 'produto')
        verbose_name = "Item do Combo"
        verbose_name_plural = "Itens do Combo"

    def __str__(self):
        return f"{self.quantity}x {self.produto.name} (Combo: {self.combo.name})"


# Relacionamento com Cliente (será definido após a criação dos apps)
# Adicionaremos via migration depois
from django.db import models as django_models

def add_cliente_relation():
    """Função para adicionar relacionamento com Cliente após criação dos apps."""
    try:
        from apps.cliente.models import Cliente
        
        # Adicionar ManyToMany para restrições alimentares
        Cliente.add_to_class(
            'alimentary_restrictions',
            models.ManyToManyField(
                RestricaoAlimentar,
                blank=True,
                verbose_name="Restrições Alimentares",
                related_name="clientes"
            )
        )
    except ImportError:
        pass  # App cliente ainda não existe

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


