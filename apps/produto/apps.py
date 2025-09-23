from django.apps import AppConfig


class ProdutoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.produto'
    verbose_name = 'Gestão de Produtos'
