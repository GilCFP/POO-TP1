from django.contrib import admin
from .models import Produto, Alimento, RestricaoAlimentar, Combo

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