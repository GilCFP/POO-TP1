"""
Módulo Produto: Define a classe abstrata Produto e suas operações.

Implementa o padrão de design Strategy para aplicação de descontos,
com encapsulamento total dos atributos via propriedades.

Author: Desenvolvimento POO TP1
Date: 2024
"""

from EntidadeBase import EntidadeBase


class Produto(EntidadeBase):
    """
    Classe abstrata que representa um produto genérico do restaurante.
    
    Implementa encapsulamento completo com getters e setters para todos os
    atributos, garantindo que as regras de negócio sejam respeitadas.
    
    Attributes:
        _name (str): Nome do produto (protegido)
        _price (float): Preço do produto (protegido)
        _available (bool): Disponibilidade do produto (protegido)
    
    Example:
        >>> alimento = Alimento("Burger", 25.00, "2024-12-31", 500)
        >>> print(alimento.name)
        'Burger'
        >>> alimento.apply_discount(0.1)  # 10% de desconto
        >>> print(alimento.price)
        22.50
    """
    
    def __init__(self, name: str, price: float, available: bool = True):
        """
        Inicializa um novo produto.
        
        Args:
            name (str): Nome do produto
            price (float): Preço do produto (deve ser positivo)
            available (bool): Se o produto está disponível (padrão: True)
            
        Raises:
            ValueError: Se o nome estiver vazio ou preço for negativo
        """
        super().__init__()
        if not name or not isinstance(name, str):
            raise ValueError("Nome do produto deve ser uma string não vazia")
        if price < 0:
            raise ValueError("Preço não pode ser negativo")
        
        self._name = name
        self._price = price
        self._available = available
    
    @property
    def name(self) -> str:
        """
        Obtém o nome do produto.
        
        Returns:
            str: O nome do produto (somente leitura)
        """
        return self._name
    
    @property
    def price(self) -> float:
        """
        Obtém o preço do produto.
        
        Returns:
            float: O preço do produto em reais (somente leitura)
        """
        return self._price
    
    @price.setter
    def price(self, novo_preco: float):
        """
        Define um novo preço para o produto.
        
        Args:
            novo_preco (float): O novo preço (deve ser positivo)
            
        Raises:
            ValueError: Se o preço for negativo
        """
        if novo_preco < 0:
            raise ValueError("Preço não pode ser negativo")
        self._price = novo_preco
    
    @property
    def available(self) -> bool:
        """
        Verifica se o produto está disponível.
        
        Returns:
            bool: True se disponível, False caso contrário (somente leitura)
        """
        return self._available
    
    @available.setter
    def available(self, disponivel: bool):
        """
        Define a disponibilidade do produto.
        
        Args:
            disponivel (bool): True para disponível, False para indisponível
        """
        if not isinstance(disponivel, bool):
            raise ValueError("Disponibilidade deve ser um booleano")
        self._available = disponivel
    
    def apply_discount(self, discount: float) -> None:
        """
        Aplica um desconto ao preço do produto.
        
        Implementa validação para garantir que o desconto está entre 0 e 1,
        representando uma porcentagem (ex: 0.1 = 10% de desconto).
        
        Args:
            discount (float): Desconto a aplicar (entre 0 e 1)
            
        Raises:
            ValueError: Se o desconto não estiver entre 0 e 1
            
        Example:
            >>> produto.apply_discount(0.15)  # 15% de desconto
        """
        if not isinstance(discount, (int, float)):
            raise ValueError("Desconto deve ser um número")
        if not 0 <= discount <= 1:
            raise ValueError("Desconto deve estar entre 0 e 1 (0% a 100%)")
        
        self._price *= (1 - discount)
    
    def validar(self) -> bool:
        """
        Valida as regras de negócio do produto.
        
        Returns:
            bool: True se o produto é válido (nome não vazio e preço positivo)
        """
        return bool(self._name) and self._price >= 0
    
    def __repr__(self) -> str:
        """
        Representação em string do produto.
        
        Returns:
            str: String formatada com informações do produto
        """
        return f"{self.__class__.__name__}(name='{self._name}', price=R${self._price:.2f}, available={self._available})"