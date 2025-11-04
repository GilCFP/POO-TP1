"""
Módulo Restaurante: Define a classe Restaurante e suas operações.

Gerencia o restaurante como um todo, incluindo cardápio, clientes,
caixa e cozinha com encapsulamento completo.

Author: Desenvolvimento POO TP1
Date: 2024
"""

from EntidadeBase import EntidadeBase
from Produto import Produto
from Cliente import Cliente
from Caixa import Caixa
from typing import List


class Restaurante(EntidadeBase):
    """
    Representa o restaurante como entidade agregadora.
    
    Gerencia o menu de produtos, clientes registrados, caixa e cozinha.
    Implementa operações de alto nível para gerenciamento do restaurante.
    
    Attributes:
        _menu (List): Menu de produtos disponíveis (protegido)
        _clients (List): Clientes registrados (protegido)
        _cash_register (Caixa): Caixa/registradora do restaurante (protegido)
    
    Example:
        >>> restaurante = Restaurante(initial_cash=1000.0)
        >>> restaurante.add_product_to_menu(produto)
        >>> restaurante.register_client(cliente)
    """
    
    def __init__(self, initial_cash: float = 0.0):
        """
        Inicializa um novo restaurante.
        
        Args:
            initial_cash (float): Valor inicial em caixa (padrão: 0.0)
            
        Raises:
            ValueError: Se o valor inicial for negativo
        """
        super().__init__()
        
        if initial_cash < 0:
            raise ValueError("Saldo inicial não pode ser negativo")
        
        self._menu: List[Produto] = []
        self._clients: List[Cliente] = []
        self._cash_register = Caixa(initial_cash)
    
    @property
    def menu(self) -> List[Produto]:
        """
        Obtém o menu de produtos disponíveis.
        
        Returns:
            List: Cópia do menu (protegido)
        """
        return self._menu.copy()
    
    @property
    def clients(self) -> List[Cliente]:
        """
        Obtém a lista de clientes registrados.
        
        Returns:
            List: Cópia da lista de clientes (protegida)
        """
        return self._clients.copy()
    
    @property
    def cash_register(self) -> Caixa:
        """
        Obtém a caixa do restaurante.
        
        Returns:
            Caixa: Referência à caixa (protegida)
        """
        return self._cash_register
    
    def add_product_to_menu(self, product: Produto) -> None:
        """
        Adiciona um produto ao menu do restaurante.
        
        Args:
            product (Produto): O produto a adicionar
            
        Raises:
            ValueError: Se o produto for inválido
            
        Example:
            >>> restaurante.add_product_to_menu(hamburguer)
        """
        if not isinstance(product, Produto):
            raise ValueError("Produto deve ser uma instância de Produto")
        
        if product in self._menu:
            raise ValueError("Este produto já está no menu")
        
        if not product.validar():
            raise ValueError("Produto inválido")
        
        self._menu.append(product)
    
    def remove_product_from_menu(self, product: Produto) -> None:
        """
        Remove um produto do menu do restaurante.
        
        Args:
            product (Produto): O produto a remover
            
        Raises:
            ValueError: Se o produto não está no menu
        """
        if product not in self._menu:
            raise ValueError("Este produto não está no menu")
        
        self._menu.remove(product)
    
    def register_client(self, client: Cliente) -> None:
        """
        Registra um novo cliente no restaurante.
        
        Args:
            client (Cliente): O cliente a registrar
            
        Raises:
            ValueError: Se o cliente for inválido ou já registrado
            
        Example:
            >>> restaurante.register_client(cliente_novo)
        """
        if not isinstance(client, Cliente):
            raise ValueError("Cliente deve ser uma instância de Cliente")
        
        if client in self._clients:
            raise ValueError("Este cliente já está registrado")
        
        if not client.validar():
            raise ValueError("Cliente inválido")
        
        self._clients.append(client)
    
    def get_product_by_name(self, product_name: str) -> Produto:
        """
        Busca um produto no menu pelo nome.
        
        Args:
            product_name (str): Nome do produto a buscar
            
        Returns:
            Produto: O produto encontrado
            
        Raises:
            ValueError: Se o produto não for encontrado
            
        Example:
            >>> burger = restaurante.get_product_by_name("Hamburger")
        """
        for product in self._menu:
            if product.name.lower() == product_name.lower():
                return product
        
        raise ValueError(f"Produto '{product_name}' não encontrado no menu")
    
    def get_client_by_name(self, client_name: str) -> Cliente:
        """
        Busca um cliente pelo nome.
        
        Args:
            client_name (str): Nome do cliente a buscar
            
        Returns:
            Cliente: O cliente encontrado
            
        Raises:
            ValueError: Se o cliente não for encontrado
            
        Example:
            >>> cliente = restaurante.get_client_by_name("João")
        """
        for client in self._clients:
            if client.name.lower() == client_name.lower():
                return client
        
        raise ValueError(f"Cliente '{client_name}' não foi encontrado")
    
    def get_menu_size(self) -> int:
        """
        Obtém o número de produtos no menu.
        
        Returns:
            int: Quantidade de produtos
        """
        return len(self._menu)
    
    def get_total_clients(self) -> int:
        """
        Obtém o número de clientes registrados.
        
        Returns:
            int: Quantidade de clientes
        """
        return len(self._clients)
    
    def validar(self) -> bool:
        """
        Valida as regras de negócio do restaurante.
        
        Returns:
            bool: True se válido (deve ter caixa)
        """
        return self._cash_register is not None
    
    def __repr__(self) -> str:
        """
        Representação em string do restaurante.
        
        Returns:
            str: String formatada com informações do restaurante
        """
        return f"Restaurante(menu_size={len(self._menu)}, " \
               f"clients={len(self._clients)}, " \
               f"revenue=R${self._cash_register.total_revenue:.2f})"