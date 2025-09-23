from django.apps import AppConfig


class PedidoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pedido'
    verbose_name = 'Gestão de Pedidos'
    
    def ready(self):
        # Importar signals quando o app estiver pronto
        # import apps.pedido.signals  # Descomente quando criar o arquivo signals
        pass
