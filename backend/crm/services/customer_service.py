"""
Customer Service Layer
Handles all business logic related to customer operations.
"""
from typing import List, Optional
from django.db.models import QuerySet
from django.utils import timezone
from ..models import Customer, GameSession
from ..serializers import CustomerSerializer


class CustomerService:
    """
    Service class for customer-related business logic.
    """
    
    @staticmethod
    def get_all_customers() -> QuerySet[Customer]:
        """Get all active customers."""
        return Customer.objects.filter(is_active=True).order_by('-registration_date')
    
    @staticmethod
    def get_customer_by_id(customer_id: int) -> Optional[Customer]:
        """Get a customer by ID."""
        try:
            return Customer.objects.get(id=customer_id, is_active=True)
        except Customer.DoesNotExist:
            return None
    
    @staticmethod
    def get_customers_by_type(customer_type: str) -> QuerySet[Customer]:
        """Get customers filtered by type."""
        return Customer.objects.filter(
            customer_type=customer_type,
            is_active=True
        ).order_by('-registration_date')
    
    @staticmethod
    def create_customer(customer_data: dict) -> Customer:
        """Create a new customer."""
        serializer = CustomerSerializer(data=customer_data)
        if serializer.is_valid():
            return serializer.save()
        raise ValueError(f"Invalid customer data: {serializer.errors}")
    
    @staticmethod
    def update_customer(customer_id: int, customer_data: dict) -> Optional[Customer]:
        """Update an existing customer."""
        customer = CustomerService.get_customer_by_id(customer_id)
        if not customer:
            return None
        
        serializer = CustomerSerializer(customer, data=customer_data, partial=True)
        if serializer.is_valid():
            return serializer.save()
        raise ValueError(f"Invalid customer data: {serializer.errors}")
    
    @staticmethod
    def deactivate_customer(customer_id: int) -> bool:
        """Soft delete a customer by marking as inactive."""
        customer = CustomerService.get_customer_by_id(customer_id)
        if customer:
            customer.is_active = False
            customer.save()
            return True
        return False
    
    @staticmethod
    def update_last_visit(customer_id: int) -> bool:
        """Update customer's last visit timestamp."""
        customer = CustomerService.get_customer_by_id(customer_id)
        if customer:
            customer.last_visit = timezone.now()
            customer.save()
            return True
        return False
    
    @staticmethod
    def get_vip_customers() -> QuerySet[Customer]:
        """Get all VIP customers."""
        return CustomerService.get_customers_by_type('VIP')
    
    @staticmethod
    def get_customer_statistics(customer_id: int) -> Optional[dict]:
        """Get customer statistics including total spent, games played, etc."""
        customer = CustomerService.get_customer_by_id(customer_id)
        if not customer:
            return None
        
        game_sessions = customer.game_sessions.all()
        total_sessions = game_sessions.count()
        total_bet = sum(session.amount_bet for session in game_sessions)
        total_won = sum(session.amount_won for session in game_sessions)
        
        return {
            'customer': customer,
            'total_sessions': total_sessions,
            'total_bet': total_bet,
            'total_won': total_won,
            'net_result': total_won - total_bet,
            'average_bet': total_bet / total_sessions if total_sessions > 0 else 0
        }
