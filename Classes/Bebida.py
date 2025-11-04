"""
Módulo Bebida: Define a classe Bebida especializada para bebidas.

Herda de Alimento e adiciona informações específicas de bebidas como
volume em ml e se é alcoólica ou não.

Author: Desenvolvimento POO TP1
Date: 2024
"""

from typing import List

from Alimento import Alimento
from RestricaoAlimentar import RestricaoAlimentar


class Bebida(Alimento):
    """
    Representa uma bebida do restaurante.
    
    Especialização de Alimento para bebidas, adicionando informações
    sobre volume, teor alcoólico e características específicas.
    
    Attributes:
        _volume_ml (int): Volume da bebida em mililitros (protegido)
        _is_alcoholic (bool): Se a bebida contém álcool (protegido)
    
    Example:
        >>> refrigerante = Bebida("Coca-Cola", 5.00, "2024-12-31", 140, 
        ...                       volume_ml=350, is_alcoholic=False)
        >>> print(refrigerante.volume_ml)
        350
    """
    
    def __init__(
        self,
        name: str,
        price: float,
        expiration_date: str,
        calories: int,
        volume_ml: int,
        is_alcoholic: bool,
        time_to_prepare: int = 0,
        available: bool = True,
        alimentary_restrictions: List[RestricaoAlimentar] = None,
        is_ingredient: bool = False
    ):
        """
        Inicializa uma nova bebida.
        
        Args:
            name (str): Nome da bebida
            price (float): Preço em reais
            expiration_date (str): Data de expiração (YYYY-MM-DD)
            calories (int): Calorias totais
            volume_ml (int): Volume em mililitros
            is_alcoholic (bool): Se contém álcool
            time_to_prepare (int): Tempo de preparo em minutos (padrão: 0)
            available (bool): Se está disponível (padrão: True)
            alimentary_restrictions (List): Restrições alimentares (padrão: vazio)
            is_ingredient (bool): Se é ingrediente (padrão: False)
            
        Raises:
            ValueError: Se volume_ml for menor que 1
        """
        if alimentary_restrictions is None:
            alimentary_restrictions = []
        
        if not isinstance(volume_ml, int) or volume_ml < 1:
            raise ValueError("Volume deve ser um inteiro positivo em mililitros")
        
        if not isinstance(is_alcoholic, bool):
            raise ValueError("is_alcoholic deve ser um booleano")
        
        super().__init__(
            name, price, expiration_date, calories,
            time_to_prepare, available, alimentary_restrictions, is_ingredient
        )
        self._volume_ml = volume_ml
        self._is_alcoholic = is_alcoholic
    
    @property
    def volume_ml(self) -> int:
        """
        Obtém o volume da bebida em mililitros.
        
        Returns:
            int: Volume em ml (somente leitura)
        """
        return self._volume_ml
    
    @property
    def is_alcoholic(self) -> bool:
        """
        Verifica se a bebida contém álcool.
        
        Returns:
            bool: True se alcoólica, False caso contrário (somente leitura)
        """
        return self._is_alcoholic
    
    def validar(self) -> bool:
        """
        Valida as regras de negócio da bebida.
        
        Returns:
            bool: True se válida (herdado + volume válido)
        """
        return super().validar() and self._volume_ml > 0
    
    def __repr__(self) -> str:
        """
        Representação em string da bebida.
        
        Returns:
            str: String formatada com informações da bebida
        """
        alcool = "Alcoólica" if self._is_alcoholic else "Sem álcool"
        return f"{self.__class__.__name__}(name='{self._name}', price=R${self._price:.2f}, " \
               f"volume={self._volume_ml}ml, {alcool})"