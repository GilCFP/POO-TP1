"""
Services para implementar a lógica de negócio do restaurante.
Esta camada contém toda a lógica de negócio e regras específicas do domínio.
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from ..models import (
    Produto, Cliente, Pedido, ItemPedido, Caixa, Cozinha, 
    Restaurante, StatusPedido, Alimento
)


class RestauranteService:
    """Service para gerenciar operações do restaurante."""
    
    @staticmethod
    def criar_restaurante(nome: str, numero_chefs: int = 1, caixa_inicial: float = 0.0):
        """Cria um novo restaurante com caixa e cozinha."""
        with transaction.atomic():
            # Criar caixa
            caixa = Caixa.objects.create(total_revenue=Decimal(str(caixa_inicial)))
            
            # Criar cozinha
            cozinha = Cozinha.objects.create(number_of_chefs=numero_chefs)
            
            # Criar restaurante
            restaurante = Restaurante.objects.create(
                name=nome,
                cash_register=caixa,
                kitchen=cozinha
            )
            
            return restaurante
    
    @staticmethod
    def adicionar_produto_ao_menu(restaurante_id: int, produto_id: int):
        """Adiciona um produto ao menu do restaurante."""
        try:
            restaurante = Restaurante.objects.get(id=restaurante_id)
            produto = Produto.objects.get(id=produto_id)
            
            if not produto.available:
                raise ValidationError("Produto não está disponível")
            
            restaurante.add_product_to_menu(produto)
            return True
        except (Restaurante.DoesNotExist, Produto.DoesNotExist):
            raise ValidationError("Restaurante ou produto não encontrado")
    
    @staticmethod
    def registrar_cliente(restaurante_id: int, cliente_id: int):
        """Registra um cliente no restaurante."""
        try:
            restaurante = Restaurante.objects.get(id=restaurante_id)
            cliente = Cliente.objects.get(id=cliente_id)
            
            restaurante.register_client(cliente)
            return True
        except (Restaurante.DoesNotExist, Cliente.DoesNotExist):
            raise ValidationError("Restaurante ou cliente não encontrado")


class ClienteService:
    """Service para gerenciar operações de clientes."""
    
    @staticmethod
    def criar_cliente(nome: str, endereco: str = "", saldo_inicial: float = 0.0):
        """Cria um novo cliente."""
        cliente = Cliente.objects.create(
            name=nome,
            address=endereco,
            balance=Decimal(str(saldo_inicial))
        )
        return cliente
    
    @staticmethod
    def adicionar_saldo(cliente_id: int, valor: float):
        """Adiciona saldo ao cliente."""
        try:
            cliente = Cliente.objects.get(id=cliente_id)
            cliente.add_funds(valor)
            return cliente
        except Cliente.DoesNotExist:
            raise ValidationError("Cliente não encontrado")
    
    @staticmethod
    def verificar_restricoes_produto(cliente_id: int, produto_id: int):
        """Verifica se o cliente pode consumir um produto."""
        try:
            cliente = Cliente.objects.get(id=cliente_id)
            produto = Produto.objects.get(id=produto_id)
            
            return cliente.can_consume(produto)
        except (Cliente.DoesNotExist, Produto.DoesNotExist):
            raise ValidationError("Cliente ou produto não encontrado")


class PedidoService:
    """Service para gerenciar operações de pedidos."""
    
    @staticmethod
    def criar_pedido(cliente_id: int):
        """Cria um novo pedido para um cliente."""
        try:
            cliente = Cliente.objects.get(id=cliente_id)
            pedido = Pedido.objects.create(cliente=cliente)
            return pedido
        except Cliente.DoesNotExist:
            raise ValidationError("Cliente não encontrado")
    
    @staticmethod
    def adicionar_item_ao_pedido(pedido_id: int, produto_id: int, quantidade: int = 1):
        """Adiciona um item ao pedido com validações de negócio."""
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            produto = Produto.objects.get(id=produto_id)
            
            # Validações de negócio
            if pedido.status != StatusPedido.ORDERING:
                raise ValidationError("Pedido não está em estado de modificação")
            
            if not produto.available:
                raise ValidationError("Produto não está disponível")
            
            # Verificar restrições alimentares
            if not ClienteService.verificar_restricoes_produto(pedido.cliente.id, produto_id):
                raise ValidationError("Cliente possui restrições alimentares para este produto")
            
            # Verificar se é alimento e está vencido
            if hasattr(produto, 'alimento') and produto.alimento.is_expired():
                raise ValidationError("Produto está vencido")
            
            pedido.add_item(produto, quantidade)
            return pedido
            
        except (Pedido.DoesNotExist, Produto.DoesNotExist):
            raise ValidationError("Pedido ou produto não encontrado")
    
    @staticmethod
    def remover_item_do_pedido(pedido_id: int, produto_id: int):
        """Remove um item do pedido."""
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            produto = Produto.objects.get(id=produto_id)
            
            if pedido.status != StatusPedido.ORDERING:
                raise ValidationError("Pedido não está em estado de modificação")
            
            pedido.remove_item(produto)
            return pedido
            
        except (Pedido.DoesNotExist, Produto.DoesNotExist):
            raise ValidationError("Pedido ou produto não encontrado")
    
    @staticmethod
    def finalizar_pedido(pedido_id: int):
        """Finaliza um pedido e move para pagamento."""
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            
            if pedido.status != StatusPedido.ORDERING:
                raise ValidationError("Pedido não está em estado de finalização")
            
            if not pedido.items.exists():
                raise ValidationError("Pedido não possui itens")
            
            # Calcular total antes de finalizar
            pedido.calculate_total()
            
            if pedido.total_price <= 0:
                raise ValidationError("Pedido deve ter valor maior que zero")
            
            return pedido
            
        except Pedido.DoesNotExist:
            raise ValidationError("Pedido não encontrado")


class PagamentoService:
    """Service para gerenciar pagamentos."""
    
    @staticmethod
    def processar_pagamento(pedido_id: int, caixa_id: int):
        """Processa o pagamento de um pedido."""
        with transaction.atomic():
            try:
                pedido = Pedido.objects.get(id=pedido_id)
                caixa = Caixa.objects.get(id=caixa_id)
                
                if pedido.status != StatusPedido.ORDERING:
                    raise ValidationError("Pedido não está pronto para pagamento")
                
                # Verificar se cliente tem saldo suficiente
                if pedido.cliente.balance < pedido.total_price:
                    raise ValidationError("Saldo insuficiente")
                
                # Processar pagamento
                caixa.process_payment(pedido.cliente, pedido)
                
                return pedido
                
            except (Pedido.DoesNotExist, Caixa.DoesNotExist):
                raise ValidationError("Pedido ou caixa não encontrado")


class CozinhaService:
    """Service para gerenciar operações da cozinha."""
    
    @staticmethod
    def adicionar_pedido_na_fila(cozinha_id: int, pedido_id: int, prioridade: bool = False):
        """Adiciona um pedido na fila da cozinha."""
        try:
            cozinha = Cozinha.objects.get(id=cozinha_id)
            pedido = Pedido.objects.get(id=pedido_id)
            
            if prioridade:
                # Implementar lógica de prioridade se necessário
                pass
            
            cozinha.add_order_to_queue(pedido)
            return True
            
        except (Cozinha.DoesNotExist, Pedido.DoesNotExist):
            raise ValidationError("Cozinha ou pedido não encontrado")
    
    @staticmethod
    def iniciar_proximo_pedido(cozinha_id: int):
        """Inicia o preparo do próximo pedido da fila."""
        try:
            cozinha = Cozinha.objects.get(id=cozinha_id)
            cozinha.start_next_order()
            return True
            
        except Cozinha.DoesNotExist:
            raise ValidationError("Cozinha não encontrada")
    
    @staticmethod
    def finalizar_pedido(cozinha_id: int, pedido_id: int):
        """Finaliza o preparo de um pedido."""
        try:
            cozinha = Cozinha.objects.get(id=cozinha_id)
            pedido = Pedido.objects.get(id=pedido_id)
            
            cozinha.complete_order(pedido)
            return True
            
        except (Cozinha.DoesNotExist, Pedido.DoesNotExist):
            raise ValidationError("Cozinha ou pedido não encontrado")


class ProdutoService:
    """Service para gerenciar produtos."""
    
    @staticmethod
    def aplicar_desconto(produto_id: int, desconto: float):
        """Aplica desconto a um produto."""
        try:
            produto = Produto.objects.get(id=produto_id)
            produto.apply_discount(desconto)
            return produto
            
        except Produto.DoesNotExist:
            raise ValidationError("Produto não encontrado")
    
    @staticmethod
    def verificar_produtos_vencidos():
        """Retorna lista de produtos vencidos."""
        produtos_vencidos = []
        alimentos = Alimento.objects.all()
        
        for alimento in alimentos:
            if alimento.is_expired():
                produtos_vencidos.append(alimento)
        
        return produtos_vencidos
    
    @staticmethod
    def desativar_produtos_vencidos():
        """Desativa automaticamente produtos vencidos."""
        produtos_vencidos = ProdutoService.verificar_produtos_vencidos()
        
        for produto in produtos_vencidos:
            produto.available = False
            produto.save()
        
        return len(produtos_vencidos)