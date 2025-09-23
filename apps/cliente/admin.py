from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'balance', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'email', 'phone', 'birth_date')
        }),
        ('Endereço', {
            'fields': ('address',)
        }),
        ('Conta', {
            'fields': ('balance', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
