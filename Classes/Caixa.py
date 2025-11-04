"""
Módulo Caixa: Define a classe Caixa (Registradora) e suas operações.

Gerencia pagamentos e receita total do restaurante com encapsulamento
completo via propriedades.

Author: Desenvolvimento POO TP1
Date: 2024
"""

from EntidadeBase import EntidadeBase
from Cliente import Cliente
from Pedido import Pedido


class Caixa(EntidadeBase):
    """
    Representa a registradora/caixa do restaurante.
    
    Gerencia transações de pagamento, receita total e controla o fluxo
    de dinheiro do restaurante.
    
    Attributes:
        _total_revenue (float): Receita acumulada em reais (protegido)
    
    Example:
        >>> caixa = Caixa(initial_cash=500.0)
        >>> caixa.process_payment(cliente)
        >>> print(caixa.total_revenue)
        525.50
    """
    
    def __init__(self, initial_cash: float = 0.0):
        """
        Inicializa a caixa do restaurante.
        
        Args:
            initial_cash (float): Valor inicial em caixa (padrão: 0.0)
            
        Raises:
            ValueError: Se o valor inicial for negativo
        """
        super().__init__()
        
        if initial_cash < 0:
            raise ValueError("Saldo inicial não pode ser negativo")
        
        self._total_revenue = initial_cash
    
    @property
    def total_revenue(self) -> float:
        """
        Obtém a receita total acumulada em caixa.
        
        Returns:
            float: Receita em reais (somente leitura)
        """
        return self._total_revenue
    
    def process_payment(self, client: Cliente) -> float:
        """
        Processa o pagamento do cliente usando o carrinho.
        
        Verifica saldo do cliente, realiza o desconto na conta dele,
        adiciona o valor à receita total, e cria novo carrinho.
        
        Args:
            client (Cliente): O cliente que está pagando
            
        Returns:
            float: O valor processado do pagamento
            
        Raises:
            ValueError: Se o cliente não tiver saldo suficiente
            
        Example:
            >>> valor_pago = caixa.process_payment(cliente)
        """
        if not isinstance(client, Cliente):
            raise ValueError("Cliente deve ser uma instância de Cliente")
        
        order_total = client.cart.get_total()
        
        if client.balance < order_total:
            raise ValueError(
                f"Saldo insuficiente. Necessário: R${order_total:.2f}, "
                f"Disponível: R${client.balance:.2f}"
            )
        
        # Processa o pagamento
        client.remove_funds(order_total)
        self._total_revenue += order_total
        
        # Cria novo carrinho vazio para o cliente
        client._cart = Pedido()
        
        return order_total
    
    def validar(self) -> bool:
        """
        Valida as regras de negócio da caixa.
        
        Returns:
            bool: True se válida (receita não negativa)
        """
        return self._total_revenue >= 0
    
    def __repr__(self) -> str:
        """
        Representação em string da caixa.
        
        Returns:
            str: String formatada com informações da caixa
        """
        return f"Caixa(total_revenue=R${self._total_revenue:.2f})"