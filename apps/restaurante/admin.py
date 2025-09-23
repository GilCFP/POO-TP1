from django.contrib import admin
from .models import Restaurante, Cozinha, Caixa, EstacaoTrabalho

@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'is_open', 'delivery_fee')
    search_fields = ('name', 'email')
    filter_horizontal = ('menu',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'address', 'phone', 'email')
        }),
        ('Operação', {
            'fields': ('is_open', 'opening_time', 'closing_time', 'delivery_fee', 'minimum_order_value')
        }),
        ('Menu', {
            'fields': ('menu',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Cozinha)
class CozinhaAdmin(admin.ModelAdmin):
    list_display = ('restaurante', 'number_of_chefs', 'number_of_stations', 'is_active')
    list_filter = ('restaurante', 'is_active')
    filter_horizontal = ('orders_in_queue',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Caixa)
class CaixaAdmin(admin.ModelAdmin):
    list_display = ('restaurante', 'total_revenue', 'daily_revenue', 'last_reset_date')
    list_filter = ('restaurante', 'last_reset_date', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informações', {
            'fields': ('restaurante',)
        }),
        ('Financeiro', {
            'fields': ('total_revenue', 'daily_revenue', 'last_reset_date', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(EstacaoTrabalho)
class EstacaoTrabalhoAdmin(admin.ModelAdmin):
    list_display = ('name', 'cozinha', 'tipo', 'is_active', 'current_order')
    list_filter = ('cozinha', 'tipo', 'is_active')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
