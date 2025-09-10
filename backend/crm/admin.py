from django.contrib import admin
from .models import Customer, GameSession


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'customer_type', 'registration_date', 'total_spent', 'is_active']
    list_filter = ['customer_type', 'is_active', 'registration_date']
    search_fields = ['first_name', 'last_name', 'email']
    readonly_fields = ['registration_date']


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'game_type', 'start_time', 'amount_bet', 'amount_won', 'net_result']
    list_filter = ['game_type', 'start_time']
    search_fields = ['customer__first_name', 'customer__last_name', 'game_type']
    readonly_fields = ['start_time']
