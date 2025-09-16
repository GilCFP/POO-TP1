from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    """Model representing a casino customer."""
    
    CUSTOMER_TYPES = (
        ('VIP', 'VIP'),
        ('REGULAR', 'Regular'),
        ('PREMIUM', 'Premium'),
    )
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    customer_type = models.CharField(max_length=10, choices=CUSTOMER_TYPES, default='REGULAR')
    registration_date = models.DateTimeField(auto_now_add=True)
    last_visit = models.DateTimeField(null=True, blank=True)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-registration_date']
        
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class GameSession(models.Model):
    """Model representing a customer's gaming session."""
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='game_sessions')
    game_type = models.CharField(max_length=50)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    amount_bet = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_won = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        ordering = ['-start_time']
        
    def __str__(self):
        return f"{self.customer.full_name} - {self.game_type}"
    
    @property
    def net_result(self):
        return self.amount_won - self.amount_bet
class Game(models.Model):
    """Model representing a casino game."""
    
    name = models.CharField(max_length=100, unique=True)

    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name