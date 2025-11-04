"""
Módulo Comida: Define a classe Comida especializada para alimentos sólidos.

Herda de Alimento e adiciona informações específicas de comidas como
quantidade de pessoas que um prato serve.

Author: Desenvolvimento POO TP1
Date: 2024
"""

from typing import Optional, List

from Alimento import Alimento
from RestricaoAlimentar import RestricaoAlimentar


class Comida(Alimento):
    """
    Representa uma comida específica do restaurante.
    
    Especialização de Alimento para comidas/pratos, adicionando informação
    sobre quantas pessoas o prato serve.
    
    Attributes:
        _persons_served (int): Número de pessoas que o prato serve (protegido)
    
    Example:
        >>> pizza = Comida("Pizza", 40.00, "2024-12-31", 800, persons_served=2)
        >>> print(pizza.persons_served)
        2
    """
    
    def __init__(
        self,
        name: str,
        price: float,
        expiration_date: str,
        calories: int,
        persons_served: int,
        time_to_prepare: int = 0,
        available: bool = True,
        alimentary_restrictions: Optional[List[RestricaoAlimentar]] = None,
        is_ingredient: bool = False
    ):
        """
        Inicializa uma nova comida.
        
        Args:
            name (str): Nome da comida
            price (float): Preço em reais
            expiration_date (str): Data de expiração (YYYY-MM-DD)
            calories (int): Calorias totais
            persons_served (int): Número de pessoas que serve
            time_to_prepare (int): Tempo de preparo em minutos (padrão: 0)
            available (bool): Se está disponível (padrão: True)
            alimentary_restrictions (List): Restrições alimentares (padrão: vazio)
            is_ingredient (bool): Se é ingrediente (padrão: False)
            
        Raises:
            ValueError: Se persons_served for menor que 1
        """
        if alimentary_restrictions is None:
            alimentary_restrictions = []
        
        if not isinstance(persons_served, int) or persons_served < 1:
            raise ValueError("Número de pessoas deve ser um inteiro positivo")
        
        super().__init__(
            name, price, expiration_date, calories,
            time_to_prepare, available, alimentary_restrictions, is_ingredient
        )
        self._persons_served = persons_served
    
    @property
    def persons_served(self) -> int:
        """
        Obtém quantas pessoas a comida serve.
        
        Returns:
            int: Número de pessoas (somente leitura)
        """
        return self._persons_served
    
    def validar(self) -> bool:
        """
        Valida as regras de negócio da comida.
        
        Returns:
            bool: True se válida (herdado + persons_served >= 1)
        """
        return super().validar() and self._persons_served >= 1
    
    def __repr__(self) -> str:
        """
        Representação em string da comida.
        
        Returns:
            str: String formatada com informações da comida
        """
        return f"{self.__class__.__name__}(name='{self._name}', price=R${self._price:.2f}, " \
               f"persons_served={self._persons_served})"