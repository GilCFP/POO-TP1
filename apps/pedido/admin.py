from django.contrib import admin
from .models import Pedido, ItemPedido, HistoricoPedido

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    min_num = 1

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('cliente__name',)
    readonly_fields = ('total_price', 'created_at', 'updated_at')
    inlines = [ItemPedidoInline]
    
    fieldsets = (
        ('Informações do Pedido', {
            'fields': ('cliente', 'status', 'delivery_address')
        }),
        ('Valores e Tempo', {
            'fields': ('total_price',)
        }),
        ('Datas', {
            'fields': ('estimated_delivery_time', 'actual_delivery_time', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'produto', 'quantidade', 'unit_price')
    list_filter = ('pedido__status',)
    search_fields = ('pedido__id', 'produto__name')

@admin.register(HistoricoPedido)
class HistoricoPedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'status_anterior', 'status_novo', 'created_at')
    list_filter = ('status_anterior', 'status_novo', 'created_at')
    search_fields = ('pedido__id',)
    readonly_fields = ('created_at',)
