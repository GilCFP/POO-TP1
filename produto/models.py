from django.db import models
from decimal import Decimal
from datetime import date

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