from django.db import models
from decimal import Decimal
from apps.core.models import TimeStampedModel


class Cliente(TimeStampedModel):
    """Representa um cliente do restaurante."""
    name = models.CharField(max_length=100, verbose_name="Nome")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.0, 
        verbose_name="Saldo"
    )
    address = models.TextField(blank=True, null=True, verbose_name="Endereço")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    
    # Relacionamento com restrições será definido no app produto
    # alimentary_restrictions será um ManyToMany para produto.RestricaoAlimentar

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

    def has_sufficient_balance(self, amount: Decimal) -> bool:
        """Verifica se o cliente tem saldo suficiente."""
        return self.balance >= amount

    def get_full_address(self):
        """Retorna o endereço completo formatado."""
        return self.address if self.address else "Endereço não informado"

    def __str__(self):
        return f"{self.name} ({self.email})"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['name']
