"""
Módulo Combo: Define a classe Combo para agrupamento de produtos.

Implementa agregação de múltiplos produtos com preço combinado e
encapsulamento completo.

Author: Desenvolvimento POO TP1
Date: 2024
"""

from EntidadeBase import EntidadeBase
from Produto import Produto
from Alimento import Alimento
from typing import List


class Combo(EntidadeBase):
    """
    Representa um combo (agrupamento) de produtos.
    
    Permite agrupar múltiplos produtos com desconto combinado,
    calculando automaticamente o preço total e tempo de preparo.
    
    Attributes:
        _name (str): Nome do combo (protegido)
        _items (List): Lista de produtos no combo (protegido)
        _price (float): Preço total do combo (protegido)
    
    Example:
        >>> burger = Alimento("Burger", 20.0, "2024-12-31", 500)
        >>> bebida = Bebida("Refrigerante", 5.0, "2024-12-31", 140, 350, False)
        >>> combo = Combo("Combo Especial", [burger, bebida])
        >>> print(combo.price)
        25.0
    """
    
    def __init__(self, name: str, items: List[Produto]):
        """
        Inicializa um novo combo.
        
        Args:
            name (str): Nome do combo
            items (List[Produto]): Lista de produtos a agrupar
            
        Raises:
            ValueError: Se nome for vazio ou lista de items inválida
        """
        super().__init__()
        
        if not name or not isinstance(name, str):
            raise ValueError("Nome do combo deve ser uma string não vazia")
        
        if not isinstance(items, list) or len(items) < 1:
            raise ValueError("Combo deve conter pelo menos um produto")
        
        for item in items:
            if not isinstance(item, Produto):
                raise ValueError("Todos os itens devem ser instâncias de Produto")
        
        self._name = name
        self._items = items.copy()
        self._price = sum(item.price for item in self._items)
    
    @property
    def name(self) -> str:
        """
        Obtém o nome do combo.
        
        Returns:
            str: Nome do combo (somente leitura)
        """
        return self._name
    
    @property
    def items(self) -> List[Produto]:
        """
        Obtém os itens do combo.
        
        Returns:
            List: Cópia da lista de itens (protegida)
        """
        return self._items.copy()
    
    @property
    def price(self) -> float:
        """
        Obtém o preço total do combo.
        
        Returns:
            float: Preço em reais (somente leitura)
        """
        return self._price
    
    def apply_discount(self, discount: float) -> None:
        """
        Aplica um desconto ao preço total do combo.
        
        Args:
            discount (float): Desconto a aplicar (entre 0 e 1)
            
        Raises:
            ValueError: Se o desconto for inválido
            
        Example:
            >>> combo.apply_discount(0.1)  # 10% de desconto
        """
        if not isinstance(discount, (int, float)):
            raise ValueError("Desconto deve ser um número")
        if not 0 <= discount <= 1:
            raise ValueError("Desconto deve estar entre 0 e 1")
        
        self._price *= (1 - discount)
    
    def get_time_to_prepare(self) -> int:
        """
        Calcula o tempo total de preparo do combo.
        
        Soma o tempo de preparo de todos os itens (alimentos) do combo.
        
        Returns:
            int: Tempo de preparo em minutos
            
        Example:
            >>> tempo = combo.get_time_to_prepare()
        """
        total_time = 0
        for item in self._items:
            if isinstance(item, Alimento):
                total_time += item.time_to_prepare
        return total_time
    
    def add_item(self, item: Produto) -> None:
        """
        Adiciona um novo item ao combo.
        
        Args:
            item (Produto): O produto a adicionar
            
        Raises:
            ValueError: Se o item for inválido
            
        Example:
            >>> combo.add_item(novo_produto)
        """
        if not isinstance(item, Produto):
            raise ValueError("Item deve ser uma instância de Produto")
        
        if item in self._items:
            raise ValueError("Este item já está no combo")
        
        self._items.append(item)
        self._price += item.price
    
    def remove_item(self, item: Produto) -> None:
        """
        Remove um item do combo.
        
        Args:
            item (Produto): O item a remover
            
        Raises:
            ValueError: Se o item não está no combo
            
        Example:
            >>> combo.remove_item(produto)
        """
        if item not in self._items:
            raise ValueError("Item não encontrado no combo")
        
        if len(self._items) <= 1:
            raise ValueError("Combo deve ter pelo menos um item")
        
        self._items.remove(item)
        self._price -= item.price
    
    def get_items_count(self) -> int:
        """
        Obtém a quantidade de itens no combo.
        
        Returns:
            int: Número de produtos
        """
        return len(self._items)
    
    def validar(self) -> bool:
        """
        Valida as regras de negócio do combo.
        
        Returns:
            bool: True se válido (nome não vazio e tem itens)
        """
        return bool(self._name) and len(self._items) > 0
    
    def __repr__(self) -> str:
        """
        Representação em string do combo.
        
        Returns:
            str: String formatada com informações do combo
        """
        return f"{self.__class__.__name__}(name='{self._name}', price=R${self._price:.2f}, " \
               f"items={len(self._items)})"
