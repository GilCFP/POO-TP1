from django.contrib import admin
from .models import (
    Produto, Alimento, RestricaoAlimentar, Combo, Bebida, Comida,
    Cliente, Pedido, ItemPedido, Caixa, Cozinha, Restaurante
)

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'available')
    list_filter = ('available',)
    search_fields = ('name',)

@admin.register(Alimento)
class AlimentoAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'available', 'expiration_date', 'is_expired', 'is_ingredient')
    list_filter = ('available', 'is_ingredient', 'alimentary_restrictions')
    search_fields = ('name',)
    filter_horizontal = ('alimentary_restrictions', 'additional_ingredients',)

@admin.register(RestricaoAlimentar)
class RestricaoAlimentarAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Combo)
class ComboAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'calculated_price', 'available', 'get_time_to_prepare')
    list_filter = ('available',)
    search_fields = ('name',)
    filter_horizontal = ('items',)
    readonly_fields = ('calculated_price', 'get_time_to_prepare')
    fieldsets = (
        (None, {'fields': ('name', 'price', 'available')}),
        ('Itens e Cálculos', {'fields': ('items', 'calculated_price', 'get_time_to_prepare')}),
    )


@admin.register(Bebida)
class BebidaAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'available', 'volume_ml', 'is_alcoholic', 'expiration_date', 'is_expired')
    list_filter = ('available', 'is_alcoholic', 'alimentary_restrictions')
    search_fields = ('name',)
    filter_horizontal = ('alimentary_restrictions', 'additional_ingredients')


@admin.register(Comida)
class ComidaAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'available', 'persons_served', 'expiration_date', 'is_expired')
    list_filter = ('available', 'alimentary_restrictions')
    search_fields = ('name',)
    filter_horizontal = ('alimentary_restrictions', 'additional_ingredients')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('name', 'balance', 'address')
    search_fields = ('name', 'address')
    filter_horizontal = ('alimentary_restrictions',)


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('cliente__name',)
    readonly_fields = ('total_price', 'created_at', 'updated_at')
    inlines = [ItemPedidoInline]
    
    fieldsets = (
        (None, {'fields': ('cliente', 'status')}),
        ('Valores', {'fields': ('total_price',)}),
        ('Datas', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Caixa)
class CaixaAdmin(admin.ModelAdmin):
    list_display = ('id', 'total_revenue', 'created_at')
    readonly_fields = ('total_revenue', 'created_at')
    list_filter = ('created_at',)


@admin.register(Cozinha)
class CozinhaAdmin(admin.ModelAdmin):
    list_display = ('id', 'number_of_chefs', 'current_capacity', 'full_capacity')
    readonly_fields = ('current_capacity', 'full_capacity')
    filter_horizontal = ('orders_in_progress', 'orders_in_queue')


@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    filter_horizontal = ('menu', 'clients')
    readonly_fields = ('created_at',)