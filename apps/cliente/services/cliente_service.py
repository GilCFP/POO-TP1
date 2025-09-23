from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from typing import Optional, Dict, Any
from ..models import Cliente
import logging

logger = logging.getLogger(__name__)


class ClienteService:
    """Service para gerenciamento de clientes."""
    
    @staticmethod
    def create_temporary_client(cpf: str, name: str, phone: str) -> Cliente:
        """
        Cria um cliente temporário.
        
        Args:
            cpf: CPF do cliente (será validado e formatado)
            name: Nome do cliente
            phone: Telefone para contato
            
        Returns:
            Cliente: Instância do cliente criado
            
        Raises:
            ValidationError: Se dados inválidos
        """
        try:
            with transaction.atomic():
                # Verifica se já existe cliente com este CPF
                existing_client = Cliente.objects.filter(cpf=cpf).first()
                if existing_client:
                    if existing_client.is_temporary:
                        # Atualiza dados do cliente temporário existente
                        existing_client.name = name
                        existing_client.phone = phone
                        existing_client.is_active = True
                        existing_client.save()
                        logger.info(f"Cliente temporário atualizado: {cpf}")
                        return existing_client
                    else:
                        raise ValidationError(
                            f"Já existe conta permanente com CPF {cpf}"
                        )
                
                # Cria novo cliente temporário
                client = Cliente(
                    cpf=cpf,
                    name=name,
                    phone=phone,
                    is_temporary=True,
                    is_active=True
                )
                client.save()
                
                logger.info(f"Cliente temporário criado: {cpf}")
                return client
                
        except Exception as e:
            logger.error(f"Erro ao criar cliente temporário {cpf}: {str(e)}")
            raise
    
    @staticmethod
    def create_permanent_client(
        cpf: str, 
        name: str, 
        phone: str, 
        email: str, 
        password: str,
        address: str = None
    ) -> Cliente:
        """
        Cria um cliente permanente.
        
        Args:
            cpf: CPF do cliente
            name: Nome completo
            phone: Telefone
            email: Email (obrigatório para contas permanentes)
            password: Senha
            address: Endereço (opcional)
            
        Returns:
            Cliente: Instância do cliente criado
        """
        try:
            with transaction.atomic():
                # Verifica se já existe cliente com este CPF
                existing_client = Cliente.objects.filter(cpf=cpf).first()
                if existing_client:
                    if existing_client.is_temporary:
                        # Converte conta temporária em permanente
                        existing_client.convert_to_permanent(password, email)
                        existing_client.name = name
                        existing_client.phone = phone
                        if address:
                            existing_client.address = address
                        existing_client.save()
                        logger.info(f"Cliente temporário convertido para permanente: {cpf}")
                        return existing_client
                    else:
                        raise ValidationError(
                            f"Já existe conta permanente com CPF {cpf}"
                        )
                
                # Verifica email único
                if Cliente.objects.filter(email=email).exists():
                    raise ValidationError(f"Email {email} já está em uso")
                
                # Cria novo cliente permanente
                client = Cliente(
                    cpf=cpf,
                    name=name,
                    phone=phone,
                    email=email,
                    address=address,
                    is_temporary=False,
                    is_active=True
                )
                client.set_password(password)
                client.save()
                
                logger.info(f"Cliente permanente criado: {cpf}")
                return client
                
        except Exception as e:
            logger.error(f"Erro ao criar cliente permanente {cpf}: {str(e)}")
            raise
    
    @staticmethod
    def authenticate_client(cpf: str, password: str = None) -> Optional[Cliente]:
        """
        Autentica cliente.
        
        Args:
            cpf: CPF do cliente
            password: Senha (apenas para contas permanentes)
            
        Returns:
            Cliente ou None se autenticação falhar
        """
        try:
            client = Cliente.objects.filter(
                cpf=Cliente.format_cpf(cpf),
                is_active=True
            ).first()
            
            if not client:
                return None
            
            # Conta temporária - apenas CPF
            if client.is_temporary:
                logger.info(f"Login temporário: {cpf}")
                return client
            
            # Conta permanente - CPF + senha
            if password and client.check_password(password):
                logger.info(f"Login permanente: {cpf}")
                return client
            
            logger.warning(f"Falha na autenticação: {cpf}")
            return None
            
        except Exception as e:
            logger.error(f"Erro na autenticação {cpf}: {str(e)}")
            return None
    
    @staticmethod
    def get_client_by_cpf(cpf: str) -> Optional[Cliente]:
        """Busca cliente por CPF."""
        try:
            return Cliente.objects.filter(
                cpf=Cliente.format_cpf(cpf),
                is_active=True
            ).first()
        except Exception as e:
            logger.error(f"Erro ao buscar cliente {cpf}: {str(e)}")
            return None
    
    @staticmethod
    def update_client_profile(
        client: Cliente, 
        data: Dict[str, Any]
    ) -> Cliente:
        """
        Atualiza perfil do cliente.
        
        Args:
            client: Instância do cliente
            data: Dados para atualização
            
        Returns:
            Cliente atualizado
        """
        try:
            with transaction.atomic():
                # Campos permitidos para atualização
                allowed_fields = ['name', 'phone', 'address', 'email']
                
                for field, value in data.items():
                    if field in allowed_fields and hasattr(client, field):
                        setattr(client, field, value)
                
                # Validação especial para email em contas permanentes
                if not client.is_temporary and 'email' in data:
                    email = data['email']
                    if Cliente.objects.filter(email=email).exclude(pk=client.pk).exists():
                        raise ValidationError(f"Email {email} já está em uso")
                
                client.save()
                logger.info(f"Perfil atualizado: {client.cpf}")
                return client
                
        except Exception as e:
            logger.error(f"Erro ao atualizar perfil {client.cpf}: {str(e)}")
            raise
    
    @staticmethod
    def cleanup_temporary_clients(days_inactive: int = 30) -> int:
        """
        Remove clientes temporários inativos.
        
        Args:
            days_inactive: Dias de inatividade para limpeza
            
        Returns:
            int: Número de clientes removidos
        """
        try:
            cutoff_date = timezone.now() - timedelta(days=days_inactive)
            
            # Busca contas temporárias inativas
            inactive_clients = Cliente.objects.filter(
                is_temporary=True,
                last_order_date__lt=cutoff_date
            )
            
            # Também inclui contas que nunca fizeram pedido
            never_ordered = Cliente.objects.filter(
                is_temporary=True,
                last_order_date__isnull=True,
                created_at__lt=cutoff_date
            )
            
            # Combina as queries
            clients_to_delete = inactive_clients.union(never_ordered)
            count = clients_to_delete.count()
            
            if count > 0:
                clients_to_delete.delete()
                logger.info(f"Removidos {count} clientes temporários inativos")
            
            return count
            
        except Exception as e:
            logger.error(f"Erro na limpeza de clientes temporários: {str(e)}")
            return 0
    
    @staticmethod
    def get_client_summary(client: Cliente) -> Dict[str, Any]:
        """
        Retorna resumo do cliente para o frontend.
        
        Args:
            client: Instância do cliente
            
        Returns:
            Dict com informações do cliente
        """
        return {
            'id': client.id,
            'cpf': client.cpf,
            'name': client.name,
            'phone': client.phone,
            'email': client.email,
            'is_temporary': client.is_temporary,
            'balance': float(client.balance),
            'address': client.address,
            'display_name': client.get_display_name(),
            'can_convert_to_permanent': client.is_temporary,
        }
