"""
Módulo Cliente: Define a classe Cliente e suas operações.

Gerencia informações de clientes, carrinho de compras, saldo e restrições alimentares
com encapsulamento total via propriedades.

Author: Desenvolvimento POO TP1
Date: 2024
"""

from EntidadeBase import EntidadeBase
from RestricaoAlimentar import RestricaoAlimentar
from StatusPedido import StatusPedido
from Produto import Produto
from Alimento import Alimento
from Pedido import Pedido
from typing import List


class Cliente(EntidadeBase):
    """
    Representa um cliente do restaurante.
    
    Gerencia informações pessoais, saldo, carrinho de compras e restrições alimentares
    do cliente. Implementa validações para garantir integridade dos dados.
    
    Attributes:
        _name (str): Nome do cliente (protegido)
        _balance (float): Saldo disponível em reais (protegido)
        _cart (Pedido): Carrinho de compras atual (protegido)
        _address (str): Endereço do cliente (protegido)
        _alimentary_restrictions (List): Restrições alimentares (protegido)
    
    Example:
        >>> cliente = Cliente("João Silva", balance=100.0)
        >>> cliente.add_alimentary_restriction(RestricaoAlimentar.VEGETARIAN)
        >>> cliente.add_funds(50.0)
        >>> print(cliente.balance)
        150.0
    """
    
    def __init__(
        self,
        name: str,
        balance: float = 0.0,
        cart: Pedido = None,
        address: str = None
    ):
        """
        Inicializa um novo cliente.
        
        Args:
            name (str): Nome do cliente
            balance (float): Saldo inicial em reais (padrão: 0.0)
            cart (Pedido): Carrinho pré-existente (padrão: novo carrinho)
            address (str): Endereço do cliente (padrão: None)
            
        Raises:
            ValueError: Se as validações falharem
        """
        super().__init__()
        
        if not name or not isinstance(name, str):
            raise ValueError("Nome do cliente deve ser uma string não vazia")
        if balance < 0:
            raise ValueError("Saldo não pode ser negativo")
        
        self._name = name
        self._balance = balance
        self._cart = cart if cart is not None else Pedido()
        self._address = address
        self._alimentary_restrictions: List[RestricaoAlimentar] = []
    
    @property
    def name(self) -> str:
        """
        Obtém o nome do cliente.
        
        Returns:
            str: Nome do cliente (somente leitura)
        """
        return self._name
    
    @property
    def balance(self) -> float:
        """
        Obtém o saldo atual do cliente.
        
        Returns:
            float: Saldo em reais (somente leitura)
        """
        return self._balance
    
    @property
    def cart(self) -> Pedido:
        """
        Obtém o carrinho de compras do cliente.
        
        Returns:
            Pedido: Referência ao carrinho (protegido)
        """
        return self._cart
    
    @property
    def address(self) -> str:
        """
        Obtém o endereço do cliente.
        
        Returns:
            str: Endereço (pode ser None)
        """
        return self._address
    
    @address.setter
    def address(self, novo_endereco: str):
        """
        Define um novo endereço para o cliente.
        
        Args:
            novo_endereco (str): Novo endereço
        """
        self._address = novo_endereco
    
    @property
    def alimentary_restrictions(self) -> List[RestricaoAlimentar]:
        """
        Obtém a lista de restrições alimentares do cliente.
        
        Returns:
            List: Cópia da lista de restrições (protegida)
        """
        return self._alimentary_restrictions.copy()
    
    def add_alimentary_restriction(self, restriction: RestricaoAlimentar) -> None:
        """
        Adiciona uma restrição alimentar ao cliente.
        
        Args:
            restriction (RestricaoAlimentar): A restrição a adicionar
            
        Raises:
            ValueError: Se a restrição já existe
            
        Example:
            >>> cliente.add_alimentary_restriction(RestricaoAlimentar.GLUTEN_FREE)
        """
        if not isinstance(restriction, RestricaoAlimentar):
            raise ValueError("Restrição deve ser do tipo RestricaoAlimentar")
        if restriction in self._alimentary_restrictions:
            raise ValueError("Esta restrição já foi adicionada")
        self._alimentary_restrictions.append(restriction)
    
    def remove_alimentary_restriction(self, restriction: RestricaoAlimentar) -> None:
        """
        Remove uma restrição alimentar do cliente.
        
        Args:
            restriction (RestricaoAlimentar): A restrição a remover
            
        Raises:
            ValueError: Se a restrição não existe
        """
        if restriction not in self._alimentary_restrictions:
            raise ValueError("Esta restrição não foi encontrada")
        self._alimentary_restrictions.remove(restriction)
    
    def clear_alimentary_restrictions(self) -> None:
        """
        Remove todas as restrições alimentares do cliente.
        """
        self._alimentary_restrictions.clear()
    
    def can_consume(self, product: Produto) -> bool:
        """
        Verifica se o cliente pode consumir um produto específico.
        
        Verifica se alguma restrição alimentar do cliente está presente no produto.
        
        Args:
            product (Produto): O produto a verificar
            
        Returns:
            bool: True se pode consumir, False se violaria restrições
            
        Example:
            >>> pode_comer = cliente.can_consume(produto_vegetariano)
        """
        if isinstance(product, Alimento):
            for restriction in self._alimentary_restrictions:
                if restriction in product.alimentary_restrictions:
                    return False
        return True
    
    def add_funds(self, amount: float) -> None:
        """
        Adiciona fundos (dinheiro) à conta do cliente.
        
        Args:
            amount (float): Valor a adicionar em reais
            
        Raises:
            ValueError: Se o valor for inválido
            
        Example:
            >>> cliente.add_funds(100.0)
        """
        if not isinstance(amount, (int, float)):
            raise ValueError("Valor deve ser um número")
        if amount <= 0:
            raise ValueError("Valor deve ser positivo")
        self._balance += amount
    
    def remove_funds(self, amount: float) -> None:
        """
        Remove fundos (realiza pagamento) da conta do cliente.
        
        Args:
            amount (float): Valor a remover em reais
            
        Raises:
            ValueError: Se o valor for inválido ou saldo insuficiente
            
        Example:
            >>> cliente.remove_funds(25.50)
        """
        if not isinstance(amount, (int, float)):
            raise ValueError("Valor deve ser um número")
        if amount <= 0:
            raise ValueError("Valor deve ser positivo")
        if amount > self._balance:
            raise ValueError(f"Saldo insuficiente. Saldo atual: R${self._balance:.2f}")
        self._balance -= amount
    
    def pay_cart(self) -> None:
        """
        Processa o pagamento do carrinho.
        
        Verifica se o cliente tem saldo suficiente e altera o status do pedido.
        
        Raises:
            ValueError: Se saldo for insuficiente
            
        Example:
            >>> cliente.pay_cart()
        """
        order_total = self._cart.get_total()
        if self._balance < order_total:
            raise ValueError(
                f"Saldo insuficiente. Necessário: R${order_total:.2f}, "
                f"Disponível: R${self._balance:.2f}"
            )
        self.remove_funds(order_total)
        self._cart.change_status(StatusPedido.PENDING_PAYMENT)
    
    def validar(self) -> bool:
        """
        Valida as regras de negócio do cliente.
        
        Returns:
            bool: True se válido (nome não vazio e saldo não negativo)
        """
        return bool(self._name) and self._balance >= 0
    
    def __repr__(self) -> str:
        """
        Representação em string do cliente.
        
        Returns:
            str: String formatada com informações do cliente
        """
        return f"Cliente(name='{self._name}', balance=R${self._balance:.2f}, " \
               f"cart_total=R${self._cart.get_total():.2f})"