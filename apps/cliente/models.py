from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from decimal import Decimal
from apps.core.models import TimeStampedModel
import re


class Cliente(TimeStampedModel):
    """Representa um cliente do restaurante."""
    
    # CPF como identificador único (obrigatório)
    cpf = models.CharField(
        max_length=14, 
        unique=True, 
        verbose_name="CPF",
        help_text="CPF no formato XXX.XXX.XXX-XX"
    )
    
    # Dados básicos
    name = models.CharField(max_length=100, verbose_name="Nome")
    phone = models.CharField(max_length=20, verbose_name="Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    
    # Conta temporária vs permanente
    is_temporary = models.BooleanField(
        default=True, 
        verbose_name="Conta Temporária",
        help_text="Contas temporárias podem ser limpas automaticamente"
    )
    password = models.CharField(
        max_length=128, 
        blank=True, 
        null=True, 
        verbose_name="Senha",
        help_text="Apenas para contas permanentes"
    )
    
    # Dados opcionais
    address = models.TextField(blank=True, null=True, verbose_name="Endereço")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    
    # Status e saldo
    balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.0, 
        verbose_name="Saldo"
    )
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    
    # Timestamps para limpeza de contas temporárias
    last_order_date = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Último Pedido"
    )
    
    @staticmethod
    def validate_cpf(cpf: str) -> bool:
        """Valida CPF usando algoritmo oficial."""
        # Remove formatação
        cpf = re.sub(r'[^0-9]', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False
            
        # Verifica se não são todos números iguais
        if cpf == cpf[0] * 11:
            return False
            
        # Calcula primeiro dígito verificador
        sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digit1 = 11 - (sum1 % 11)
        if digit1 >= 10:
            digit1 = 0
            
        # Calcula segundo dígito verificador
        sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digit2 = 11 - (sum2 % 11)
        if digit2 >= 10:
            digit2 = 0
            
        return cpf[-2:] == f"{digit1}{digit2}"
    
    @staticmethod
    def format_cpf(cpf: str) -> str:
        """Formata CPF no padrão XXX.XXX.XXX-XX."""
        cpf = re.sub(r'[^0-9]', '', cpf)
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cpf
    
    def set_password(self, raw_password: str):
        """Define senha para conta permanente."""
        if not self.is_temporary:
            self.password = make_password(raw_password)
        else:
            raise ValueError("Contas temporárias não podem ter senha")
    
    def check_password(self, raw_password: str) -> bool:
        """Verifica senha para conta permanente."""
        if self.is_temporary or not self.password:
            return False
        return check_password(raw_password, self.password)
    
    def convert_to_permanent(self, password: str, email: str = None):
        """Converte conta temporária em permanente."""
        if not self.is_temporary:
            raise ValueError("Cliente já possui conta permanente")
            
        self.is_temporary = False
        self.set_password(password)
        if email:
            self.email = email
        self.save()
    
    def can_be_cleaned(self, days_inactive: int = 30) -> bool:
        """Verifica se conta temporária pode ser limpa."""
        if not self.is_temporary:
            return False
            
        if not self.last_order_date:
            # Se nunca fez pedido, pode limpar baseado na data de criação
            from django.utils import timezone
            from datetime import timedelta
            return self.created_at < timezone.now() - timedelta(days=days_inactive)
        
        from django.utils import timezone
        from datetime import timedelta
        return self.last_order_date < timezone.now() - timedelta(days=days_inactive)

    
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
    
    def get_display_name(self):
        """Retorna nome para exibição."""
        if self.is_temporary:
            return f"{self.name} (Temp)"
        return self.name
    
    def update_last_order(self):
        """Atualiza timestamp do último pedido."""
        from django.utils import timezone
        self.last_order_date = timezone.now()
        self.save(update_fields=['last_order_date'])

    def clean(self):
        """Validação do modelo."""
        super().clean()
        
        # Valida CPF
        if not self.validate_cpf(self.cpf):
            from django.core.exceptions import ValidationError
            raise ValidationError({'cpf': 'CPF inválido'})
        
        # Formata CPF
        self.cpf = self.format_cpf(self.cpf)
        
        # Valida regras de conta temporária vs permanente
        if not self.is_temporary and not self.email:
            from django.core.exceptions import ValidationError
            raise ValidationError({'email': 'Email é obrigatório para contas permanentes'})

    def save(self, *args, **kwargs):
        """Override do save para validação automática."""
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        status = "Temp" if self.is_temporary else "Perm"
        return f"{self.name} ({self.cpf}) [{status}]"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['name']
        indexes = [
            models.Index(fields=['cpf']),
            models.Index(fields=['is_temporary', 'last_order_date']),
        ]
