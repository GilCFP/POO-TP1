from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.urls import reverse
from apps.cliente.models import Cliente
import logging

logger = logging.getLogger(__name__)


class ClienteAuthMiddleware(MiddlewareMixin):
    """
    Middleware para gerenciar autenticação de clientes.
    """
    
    # URLs que não precisam de autenticação
    EXEMPT_URLS = [
        '/api/clientes/create-temporary/',
        '/api/clientes/create-permanent/',
        '/api/clientes/login/',
        '/api/clientes/current/',
        '/admin/',
        '/static/',
        '/media/',
    ]
    
    def process_request(self, request):
        """Processa request para adicionar dados do cliente."""
        
        # Verifica se a URL precisa de autenticação
        if any(request.path.startswith(url) for url in self.EXEMPT_URLS):
            return None
        
        # Adiciona dados do cliente autenticado
        client_id = request.session.get('client_id')
        
        if client_id:
            try:
                client = Cliente.objects.get(id=client_id, is_active=True)
                request.client = client
                request.is_client_authenticated = True
                
                # Atualiza last_activity na sessão
                from django.utils import timezone
                request.session['last_activity'] = timezone.now().isoformat()
                
            except Cliente.DoesNotExist:
                # Cliente não existe mais, limpa sessão
                request.session.flush()
                request.client = None
                request.is_client_authenticated = False
        else:
            request.client = None
            request.is_client_authenticated = False
        
        return None
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Verifica autenticação antes da view."""
        
        # URLs que exigem autenticação
        protected_paths = [
            '/pedidos/',
            '/api/pedidos/',
        ]
        
        # Verifica se precisa de autenticação
        needs_auth = any(request.path.startswith(path) for path in protected_paths)
        
        if needs_auth and not getattr(request, 'is_client_authenticated', False):
            if request.content_type == 'application/json' or request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Autenticação requerida',
                    'code': 'AUTHENTICATION_REQUIRED'
                }, status=401)
            else:
                # Para páginas HTML, redireciona para login
                from django.shortcuts import redirect
                return redirect('/login/')  # Implementar página de login
        
        return None


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Middleware para segurança de sessão.
    """
    
    def process_request(self, request):
        """Processa request para verificar segurança da sessão."""
        
        # Verifica timeout de sessão (30 minutos para temporárias, 24h para permanentes)
        if 'client_id' in request.session:
            from django.utils import timezone
            from datetime import timedelta
            
            last_activity = request.session.get('last_activity')
            client_type = request.session.get('client_type', 'temporary')
            
            if last_activity:
                last_activity_time = timezone.datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                
                # Define timeout baseado no tipo de conta
                if client_type == 'temporary':
                    timeout = timedelta(minutes=30)
                else:
                    timeout = timedelta(hours=24)
                
                if timezone.now() - last_activity_time > timeout:
                    # Sessão expirada
                    logger.info(f"Sessão expirada para cliente {request.session.get('client_id')}")
                    request.session.flush()
        
        return None