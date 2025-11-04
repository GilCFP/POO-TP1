"""
Módulo Pedido: Define a classe Pedido e suas operações.

Gerencia pedidos do cliente com controle de status, itens e preço total
com encapsulamento completo.

Author: Desenvolvimento POO TP1
Date: 2024
"""

from EntidadeBase import EntidadeBase
from StatusPedido import StatusPedido
from typing import List


class Pedido(EntidadeBase):
    """
    Representa um pedido realizado por um cliente.
    
    Gerencia itens do pedido, preço total e status com validações
    para garantir consistência do fluxo de pedidos.
    
    Attributes:
        _items (List): Lista de itens no pedido (protegido)
        _total_price (float): Preço total do pedido (protegido)
        _status (StatusPedido): Status atual do pedido (protegido)
    
    Example:
        >>> pedido = Pedido()
        >>> pedido.add_item(produto1)
        >>> pedido.change_status(StatusPedido.PENDING_PAYMENT)
        >>> print(pedido.total)
        25.50
    """
    
    def __init__(
        self,
        status: StatusPedido = StatusPedido.ORDERING,
        id: int = None
    ):
        """
        Inicializa um novo pedido.
        
        Args:
            status (StatusPedido): Status inicial do pedido (padrão: ORDERING)
            id (int): ID do pedido (opcional, gerado automaticamente)
        """
        super().__init__()
        self._items: List = []
        self._total_price: float = 0.0
        self._status: StatusPedido = status
        if id is not None:
            self._id = id
    
    @property
    def items(self) -> List:
        """
        Obtém a lista de itens do pedido.
        
        Returns:
            List: Cópia da lista de itens (protegida)
        """
        return self._items.copy()
    
    @property
    def total_price(self) -> float:
        """
        Obtém o preço total do pedido.
        
        Returns:
            float: Preço total em reais (somente leitura)
        """
        return self._total_price
    
    @property
    def status(self) -> StatusPedido:
        """
        Obtém o status atual do pedido.
        
        Returns:
            StatusPedido: Status do pedido (somente leitura)
        """
        return self._status
    
    def add_item(self, item) -> None:
        """
        Adiciona um item ao pedido.
        
        Args:
            item: O produto/item a adicionar
            
        Raises:
            ValueError: Se o item for inválido
            
        Example:
            >>> pedido.add_item(produto)
        """
        if item is None:
            raise ValueError("Item não pode ser None")
        if not hasattr(item, 'price'):
            raise ValueError("Item deve ter atributo 'price'")
        
        self._items.append(item)
        self._total_price += item.price
    
    def remove_item(self, item) -> None:
        """
        Remove um item do pedido.
        
        Args:
            item: O item a remover
            
        Raises:
            ValueError: Se o item não estiver no pedido
            
        Example:
            >>> pedido.remove_item(produto)
        """
        if item not in self._items:
            raise ValueError("Item não encontrado neste pedido")
        
        self._items.remove(item)
        self._total_price -= item.price
    
    def change_status(self, new_status: StatusPedido) -> None:
        """
        Altera o status do pedido.
        
        Implementa validação para garantir fluxo correto de status:
        - Não permite voltar para status anterior (exceto CANCELED)
        - Valida transições válidas
        
        Args:
            new_status (StatusPedido): Novo status
            
        Raises:
            ValueError: Se a transição for inválida
            
        Example:
            >>> pedido.change_status(StatusPedido.PENDING_PAYMENT)
        """
        if not isinstance(new_status, StatusPedido):
            raise ValueError("Status deve ser do tipo StatusPedido")
        
        if new_status < self._status and new_status != StatusPedido.CANCELED:
            raise ValueError(
                f"Não é permitido voltar de {self._status.name} para {new_status.name}"
            )
        
        self._status = new_status
    
    def go_to_next_status(self) -> None:
        """
        Avança o pedido para o próximo status na sequência.
        
        Raises:
            ValueError: Se o pedido estiver em status final ou cancelado
            
        Example:
            >>> pedido.go_to_next_status()  # ORDERING -> PENDING_PAYMENT
        """
        if self._status == StatusPedido.CANCELED:
            raise ValueError("Não é possível alterar status de um pedido cancelado")
        elif self._status == StatusPedido.DELIVERED:
            raise ValueError("Pedido já foi entregue")
        else:
            try:
                self._status = StatusPedido(self._status.value + 1)
            except ValueError:
                raise ValueError("Não há próximo status disponível")
    
    def get_total(self) -> float:
        """
        Obtém o valor total do pedido.
        
        Returns:
            float: Preço total em reais
            
        Example:
            >>> total = pedido.get_total()
        """
        return self._total_price
    
    def validar(self) -> bool:
        """
        Valida as regras de negócio do pedido.
        
        Returns:
            bool: True se válido (total não negativo)
        """
        return self._total_price >= 0
    
    def __repr__(self) -> str:
        """
        Representação em string do pedido.
        
        Returns:
            str: String formatada com informações do pedido
        """
        return f"Pedido(id={self._id}, status={self._status.name}, " \
               f"total=R${self._total_price:.2f}, items={len(self._items)})"