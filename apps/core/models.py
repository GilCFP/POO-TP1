from django.db import models
from decimal import Decimal


class TimeStampedModel(models.Model):
    """Model abstrato para adicionar timestamps a todas as entidades."""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        abstract = True


class BaseService:
    """Classe base para todos os services do sistema."""
    
    @staticmethod
    def validate_positive_amount(amount, field_name="valor"):
        """Valida se um valor é positivo."""
        if amount <= 0:
            raise ValueError(f"{field_name} deve ser maior que zero")
    
    @staticmethod
    def validate_non_negative_amount(amount, field_name="valor"):
        """Valida se um valor não é negativo."""
        if amount < 0:
            raise ValueError(f"{field_name} não pode ser negativo")


class StatusChoicesMixin:
    """Mixin para facilitar a criação de choices de status."""
    
    @classmethod
    def get_choices(cls):
        """Retorna as choices do enum para uso em models."""
        return [(item.value, item.name.replace('_', ' ').title()) for item in cls]


class SoftDeleteModel(models.Model):
    """Model abstrato para soft delete."""
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Excluído em")

    class Meta:
        abstract = True

    def soft_delete(self):
        """Marca o registro como excluído sem remover do banco."""
        from django.utils import timezone
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restaura um registro marcado como excluído."""
        self.is_active = True
        self.deleted_at = None
        self.save()
