"""
Módulo Cozinha: Define a classe Cozinha e suas operações.

Gerencia a fila de pedidos, pedidos em progresso e capacidade da cozinha
com encapsulamento completo e validações.

Author: Desenvolvimento POO TP1
Date: 2024
"""

from EntidadeBase import EntidadeBase
from Pedido import Pedido
from StatusPedido import StatusPedido
from typing import Dict, List


class Cozinha(EntidadeBase):
    """
    Representa a cozinha do restaurante.
    
    Gerencia fila de pedidos, pedidos em preparação, e capacidade de chefes.
    Implementa validações para garantir que a capacidade não seja excedida.
    
    Attributes:
        _orders_in_progress (Dict): Dicionário de pedidos sendo preparados (protegido)
        _orders_in_queue (List): Fila de pedidos aguardando preparo (protegido)
        _number_of_chefs (int): Número de chefes disponíveis (protegido)
        _number_of_orders_in_progress (int): Quantidade de pedidos sendo preparados (protegido)
    
    Example:
        >>> cozinha = Cozinha(number_of_chefs=3)
        >>> cozinha.add_order_to_queue(pedido)
        >>> cozinha.start_next_order()
        >>> cozinha.complete_order(pedido)
    """
    
    def __init__(self, number_of_chefs: int = 1):
        """
        Inicializa a cozinha.
        
        Args:
            number_of_chefs (int): Número de chefes (capacidade máxima) - padrão: 1
            
        Raises:
            ValueError: Se number_of_chefs for menor que 1
        """
        super().__init__()
        
        if not isinstance(number_of_chefs, int) or number_of_chefs < 1:
            raise ValueError("Número de chefes deve ser um inteiro positivo")
        
        self._orders_in_progress: Dict[int, Pedido] = {}
        self._orders_in_queue: List[Pedido] = []
        self._number_of_chefs = number_of_chefs
        self._number_of_orders_in_progress = 0
    
    @property
    def orders_in_progress(self) -> Dict[int, Pedido]:
        """
        Obtém os pedidos em andamento.
        
        Returns:
            Dict: Cópia do dicionário de pedidos em progresso (protegido)
        """
        return self._orders_in_progress.copy()
    
    @property
    def orders_in_queue(self) -> List[Pedido]:
        """
        Obtém a fila de pedidos.
        
        Returns:
            List: Cópia da fila de pedidos (protegida)
        """
        return self._orders_in_queue.copy()
    
    @property
    def number_of_chefs(self) -> int:
        """
        Obtém o número de chefes (capacidade).
        
        Returns:
            int: Número de chefes (somente leitura)
        """
        return self._number_of_chefs
    
    @property
    def number_of_orders_in_progress(self) -> int:
        """
        Obtém a quantidade de pedidos sendo preparados.
        
        Returns:
            int: Número de pedidos em progresso (somente leitura)
        """
        return self._number_of_orders_in_progress
    
    @property
    def full_capacity(self) -> int:
        """
        Obtém a capacidade total da cozinha.
        
        Returns:
            int: Capacidade máxima (mesmo que number_of_chefs)
        """
        return self._number_of_chefs
    
    def is_at_full_capacity(self) -> bool:
        """
        Verifica se a cozinha está em capacidade máxima.
        
        Returns:
            bool: True se está cheia, False caso contrário
        """
        return self._number_of_orders_in_progress >= self._number_of_chefs
    
    def start_next_order(self) -> Pedido:
        """
        Inicia o preparo do próximo pedido da fila.
        
        Remove o pedido da fila, adiciona aos pedidos em progresso,
        e avança seu status para PREPARING.
        
        Returns:
            Pedido: O pedido que começou a ser preparado
            
        Raises:
            ValueError: Se cozinha está cheia ou fila está vazia
            
        Example:
            >>> pedido = cozinha.start_next_order()
        """
        if self.is_at_full_capacity():
            raise ValueError(
                f"Cozinha está em capacidade máxima ({self._number_of_chefs} chefes)"
            )
        
        if not self._orders_in_queue:
            raise ValueError("Nenhum pedido na fila para iniciar")
        
        order = self._orders_in_queue.pop(0)
        order.go_to_next_status()
        self._orders_in_progress[order.id] = order
        self._number_of_orders_in_progress += 1
        
        return order
    
    def add_order_to_queue(self, order: Pedido) -> None:
        """
        Adiciona um pedido à fila de espera.
        
        Args:
            order (Pedido): O pedido a adicionar
            
        Raises:
            ValueError: Se o pedido não estiver no status correto
            
        Example:
            >>> cozinha.add_order_to_queue(pedido)
        """
        if not isinstance(order, Pedido):
            raise ValueError("Order deve ser uma instância de Pedido")
        
        if order.status != StatusPedido.PENDING_PAYMENT:
            raise ValueError(
                f"Apenas pedidos com status PENDING_PAYMENT podem ser adicionados à fila. "
                f"Status atual: {order.status.name}"
            )
        
        self._orders_in_queue.append(order)
    
    def add_priority_order_to_queue(self, order: Pedido) -> None:
        """
        Adiciona um pedido com prioridade ao início da fila.
        
        Args:
            order (Pedido): O pedido prioritário a adicionar
            
        Raises:
            ValueError: Se o pedido não estiver no status correto
            
        Example:
            >>> cozinha.add_priority_order_to_queue(pedido_vip)
        """
        if not isinstance(order, Pedido):
            raise ValueError("Order deve ser uma instância de Pedido")
        
        if order.status != StatusPedido.PENDING_PAYMENT:
            raise ValueError(
                f"Apenas pedidos com status PENDING_PAYMENT podem ser adicionados à fila. "
                f"Status atual: {order.status.name}"
            )
        
        self._orders_in_queue.insert(0, order)
    
    def complete_order(self, order: Pedido) -> None:
        """
        Marca um pedido como completo.
        
        Remove o pedido dos pedidos em progresso, decrementa o contador,
        e avança o status para READY.
        
        Args:
            order (Pedido): O pedido a marcar como completo
            
        Raises:
            ValueError: Se o pedido não está sendo preparado
            
        Example:
            >>> cozinha.complete_order(pedido)
        """
        if order.id not in self._orders_in_progress:
            raise ValueError(f"Pedido {order.id} não encontrado nos pedidos em progresso")
        
        del self._orders_in_progress[order.id]
        self._number_of_orders_in_progress -= 1
        order.go_to_next_status()
    
    def get_queue_size(self) -> int:
        """
        Obtém o número de pedidos na fila.
        
        Returns:
            int: Quantidade de pedidos aguardando preparo
        """
        return len(self._orders_in_queue)
    
    def get_available_capacity(self) -> int:
        """
        Obtém a capacidade disponível para novos pedidos.
        
        Returns:
            int: Número de slots disponíveis para começar novos pedidos
        """
        return self._number_of_chefs - self._number_of_orders_in_progress
    
    def validar(self) -> bool:
        """
        Valida as regras de negócio da cozinha.
        
        Returns:
            bool: True se válida (número de chefes >= 1)
        """
        return self._number_of_chefs >= 1
    
    def __repr__(self) -> str:
        """
        Representação em string da cozinha.
        
        Returns:
            str: String formatada com informações da cozinha
        """
        return f"Cozinha(chefs={self._number_of_chefs}, " \
               f"em_progresso={self._number_of_orders_in_progress}, " \
               f"na_fila={len(self._orders_in_queue)})"