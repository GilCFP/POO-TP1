from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.contrib.sessions.models import Session
from django.utils import timezone
from .services.cliente_service import ClienteService
from .models import Cliente
import json
import logging

logger = logging.getLogger(__name__)


def login_page(request):
    """Renderiza a página de login React."""
    return render(request, 'cliente/client/login.html')


def register_page(request):
    """Renderiza a página de registro React."""
    return render(request, 'cliente/client/register.html')


@require_http_methods(["POST"])
@csrf_exempt
def create_temporary_client(request):
    """Cria cliente temporário com CPF e telefone."""
    try:
        data = json.loads(request.body)
        cpf = data.get('cpf')
        name = data.get('name')
        phone = data.get('phone')
        
        if not all([cpf, name, phone]):
            return JsonResponse({
                'success': False,
                'error': 'CPF, nome e telefone são obrigatórios'
            }, status=400)
        
        # Cria cliente temporário
        client = ClienteService.create_temporary_client(cpf, name, phone)
        
        # Cria sessão
        request.session['client_id'] = client.id
        request.session['client_type'] = 'temporary'
        request.session['login_time'] = timezone.now().isoformat()
        
        return JsonResponse({
            'success': True,
            'message': 'Cliente temporário criado com sucesso',
            'data': {
                'client': ClienteService.get_client_summary(client),
                'session': {
                    'session_id': request.session.session_key,
                    'type': 'temporary',
                    'login_time': request.session['login_time']
                }
            }
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Erro ao criar cliente temporário: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Erro interno do servidor'
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def create_permanent_client(request):
    """Cria cliente permanente com todos os dados."""
    try:
        data = json.loads(request.body)
        cpf = data.get('cpf')
        name = data.get('name')
        phone = data.get('phone')
        email = data.get('email')
        password = data.get('password')
        address = data.get('address')
        
        if not all([cpf, name, phone, email, password]):
            return JsonResponse({
                'error': 'CPF, nome, telefone, email e senha são obrigatórios'
            }, status=400)
        
        # Cria cliente permanente
        client = ClienteService.create_permanent_client(
            cpf=cpf,
            name=name,
            phone=phone,
            email=email,
            password=password,
            address=address
        )
        
        # Cria sessão
        request.session['client_id'] = client.id
        request.session['client_type'] = 'permanent'
        request.session['login_time'] = timezone.now().isoformat()
        
        return JsonResponse({
            'success': True,
            'client': ClienteService.get_client_summary(client),
            'session_id': request.session.session_key
        })
        
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.error(f"Erro ao criar cliente permanente: {str(e)}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def login_client(request):
    """Login do cliente (temporário ou permanente)."""
    try:
        data = json.loads(request.body)
        cpf = data.get('cpf')
        password = data.get('password')  # Opcional para contas temporárias
        
        if not cpf:
            return JsonResponse({
                'success': False,
                'error': 'CPF é obrigatório'
            }, status=400)
        
        # Autentica cliente
        client = ClienteService.authenticate_client(cpf, password)
        
        if not client:
            return JsonResponse({
                'success': False,
                'error': 'CPF ou senha inválidos'
            }, status=401)
        
        # Cria sessão
        request.session['client_id'] = client.id
        request.session['client_type'] = 'temporary' if client.is_temporary else 'permanent'
        request.session['login_time'] = timezone.now().isoformat()
        
        return JsonResponse({
            'success': True,
            'message': 'Login realizado com sucesso',
            'data': {
                'client': ClienteService.get_client_summary(client),
                'session': {
                    'session_id': request.session.session_key,
                    'type': 'temporary' if client.is_temporary else 'permanent',
                    'login_time': request.session['login_time']
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Erro interno do servidor'
        }, status=500)


@require_http_methods(["POST"])
def logout_client(request):
    """Logout do cliente."""
    try:
        if 'client_id' in request.session:
            client_id = request.session['client_id']
            request.session.flush()
            logger.info(f"Cliente {client_id} deslogado")
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        logger.error(f"Erro no logout: {str(e)}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


@require_http_methods(["GET"])
def get_current_client(request):
    """Retorna dados do cliente atual na sessão."""
    try:
        client_id = request.session.get('client_id')
        
        if not client_id:
            return JsonResponse({
                'authenticated': False,
                'client': None
            })
        
        try:
            client = Cliente.objects.get(id=client_id, is_active=True)
            return JsonResponse({
                'authenticated': True,
                'client': ClienteService.get_client_summary(client),
                'session_info': {
                    'type': request.session.get('client_type'),
                    'login_time': request.session.get('login_time')
                }
            })
        except Cliente.DoesNotExist:
            # Cliente não existe mais, limpa sessão
            request.session.flush()
            return JsonResponse({
                'authenticated': False,
                'client': None
            })
            
    except Exception as e:
        logger.error(f"Erro ao buscar cliente atual: {str(e)}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


@require_http_methods(["PUT"])
@csrf_exempt
def update_client_profile(request):
    """Atualiza perfil do cliente logado."""
    try:
        client_id = request.session.get('client_id')
        
        if not client_id:
            return JsonResponse({'error': 'Cliente não autenticado'}, status=401)
        
        try:
            client = Cliente.objects.get(id=client_id, is_active=True)
        except Cliente.DoesNotExist:
            return JsonResponse({'error': 'Cliente não encontrado'}, status=404)
        
        data = json.loads(request.body)
        
        # Atualiza perfil
        updated_client = ClienteService.update_client_profile(client, data)
        
        return JsonResponse({
            'success': True,
            'client': ClienteService.get_client_summary(updated_client)
        })
        
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.error(f"Erro ao atualizar perfil: {str(e)}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def convert_to_permanent(request):
    """Converte conta temporária em permanente."""
    try:
        client_id = request.session.get('client_id')
        
        if not client_id:
            return JsonResponse({'error': 'Cliente não autenticado'}, status=401)
        
        try:
            client = Cliente.objects.get(id=client_id, is_active=True)
        except Cliente.DoesNotExist:
            return JsonResponse({'error': 'Cliente não encontrado'}, status=404)
        
        if not client.is_temporary:
            return JsonResponse({'error': 'Cliente já possui conta permanente'}, status=400)
        
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return JsonResponse({
                'error': 'Email e senha são obrigatórios'
            }, status=400)
        
        # Converte para permanente
        client.convert_to_permanent(password, email)
        
        # Atualiza sessão
        request.session['client_type'] = 'permanent'
        
        return JsonResponse({
            'success': True,
            'client': ClienteService.get_client_summary(client)
        })
        
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.error(f"Erro ao converter conta: {str(e)}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


# Placeholder views para compatibilidade
def cliente_list(request):
    return JsonResponse({'message': 'Cliente list view'})


def create_cliente(request):
    return JsonResponse({'message': 'Create cliente view'})


def login_view(request):
    return JsonResponse({'message': 'Login view'})


def logout_view(request):
    return JsonResponse({'message': 'Logout view'})

