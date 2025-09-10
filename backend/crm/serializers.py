from rest_framework import serializers
from .models import Customer, GameSession


class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Customer
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'customer_type', 'registration_date', 'last_visit', 'total_spent',
            'is_active', 'notes'
        ]


class GameSessionSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    net_result = serializers.ReadOnlyField()
    
    class Meta:
        model = GameSession
        fields = [
            'id', 'customer', 'customer_name', 'game_type', 'start_time',
            'end_time', 'amount_bet', 'amount_won', 'net_result'
        ]