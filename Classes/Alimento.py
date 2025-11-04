"""
Módulo Alimento: Define a classe Alimento e suas operações específicas.

Representa um alimento no sistema com suporte a restrições alimentares,
data de expiração, calorias e tempo de preparo.

Author: Desenvolvimento POO TP1
Date: 2024
"""

from Produto import Produto
from RestricaoAlimentar import RestricaoAlimentar
from typing import List


class Alimento(Produto):
    """
    Representa um alimento específico com propriedades nutricionais e de preparo.
    
    Herda de Produto e adiciona funcionalidades específicas de alimentos como
    data de expiração, restrições alimentares, calorias e composição de ingredientes.
    
    Attributes:
        _expiration_date (str): Data de expiração no formato YYYY-MM-DD (protegido)
        _calories (int): Quantidade de calorias do alimento (protegido)
        _time_to_prepare (int): Tempo de preparo em minutos (protegido)
        _alimentary_restrictions (List): Restrições alimentares (protegido)
        _is_ingredient (bool): Se é um ingrediente (protegido)
        _additional_ingredients (List): Ingredientes adicionais (protegido)
    
    Example:
        >>> alimento = Alimento("Burger", 25.00, "2024-12-31", 500, 15)
        >>> print(alimento.time_to_prepare)
        15
        >>> alimento.is_expired("2024-12-25")
        False
    """
    
    def __init__(
        self,
        name: str,
        price: float,
        expiration_date: str,
        calories: int,
        time_to_prepare: int = 0,
        available: bool = True,
        alimentary_restrictions: List[RestricaoAlimentar] = None,
        is_ingredient: bool = False
    ):
        """
        Inicializa um novo alimento.
        
        Args:
            name (str): Nome do alimento
            price (float): Preço do alimento
            expiration_date (str): Data de expiração no formato YYYY-MM-DD
            calories (int): Quantidade de calorias
            time_to_prepare (int): Tempo de preparo em minutos (padrão: 0)
            available (bool): Se o alimento está disponível (padrão: True)
            alimentary_restrictions (List): Lista de restrições alimentares (padrão: vazio)
            is_ingredient (bool): Se é um ingrediente (padrão: False)
            
        Raises:
            ValueError: Se as validações falharem
        """
        super().__init__(name, price, available)
        
        if not expiration_date or not isinstance(expiration_date, str):
            raise ValueError("Data de expiração deve ser uma string válida (YYYY-MM-DD)")
        if not isinstance(calories, int) or calories < 0:
            raise ValueError("Calorias deve ser um inteiro não negativo")
        if not isinstance(time_to_prepare, int) or time_to_prepare < 0:
            raise ValueError("Tempo de preparo deve ser um inteiro não negativo")
        
        self._expiration_date = expiration_date
        self._calories = calories
        self._time_to_prepare = time_to_prepare
        self._alimentary_restrictions = alimentary_restrictions if alimentary_restrictions else []
        self._is_ingredient = is_ingredient
        self._additional_ingredients: List['Alimento'] = []
    
    @property
    def expiration_date(self) -> str:
        """
        Obtém a data de expiração do alimento.
        
        Returns:
            str: Data no formato YYYY-MM-DD (somente leitura)
        """
        return self._expiration_date
    
    @property
    def calories(self) -> int:
        """
        Obtém a quantidade de calorias do alimento.
        
        Returns:
            int: Número de calorias (somente leitura)
        """
        return self._calories
    
    @property
    def time_to_prepare(self) -> int:
        """
        Obtém o tempo de preparo do alimento em minutos.
        
        Returns:
            int: Tempo de preparo em minutos (somente leitura)
        """
        return self._time_to_prepare
    
    @property
    def alimentary_restrictions(self) -> List[RestricaoAlimentar]:
        """
        Obtém a lista de restrições alimentares do alimento.
        
        Returns:
            List: Cópia da lista de restrições (protegida)
        """
        return self._alimentary_restrictions.copy()
    
    @property
    def is_ingredient(self) -> bool:
        """
        Verifica se o alimento é um ingrediente.
        
        Returns:
            bool: True se é ingrediente, False caso contrário (somente leitura)
        """
        return self._is_ingredient
    
    @property
    def additional_ingredients(self) -> List['Alimento']:
        """
        Obtém a lista de ingredientes adicionais.
        
        Returns:
            List: Cópia da lista de ingredientes adicionais (protegida)
        """
        return self._additional_ingredients.copy()
    
    def is_expired(self, current_date: str) -> bool:
        """
        Verifica se o alimento expirou em uma data específica.
        
        Args:
            current_date (str): Data para verificação no formato YYYY-MM-DD
            
        Returns:
            bool: True se expirado, False caso contrário
            
        Example:
            >>> alimento.is_expired("2024-12-25")
            False
        """
        if not isinstance(current_date, str):
            raise ValueError("Data deve ser uma string no formato YYYY-MM-DD")
        return current_date > self._expiration_date
    
    def add_ingredient(self, ingredient: 'Alimento') -> None:
        """
        Adiciona um ingrediente ao alimento.
        
        Implementa validações para garantir que:
        - O alimento atual não é um ingrediente
        - O ingrediente a adicionar é marcado como ingrediente
        - Atualiza corretamente calorias e restrições
        
        Args:
            ingredient (Alimento): O ingrediente a adicionar
            
        Raises:
            ValueError: Se violarem as regras de negócio
            
        Example:
            >>> queijo = Alimento("Queijo", 5.0, "2024-12-31", 100, is_ingredient=True)
            >>> burger.add_ingredient(queijo)
        """
        if self._is_ingredient:
            raise ValueError("Não é possível adicionar ingredientes a um ingrediente")
        
        if not ingredient.is_ingredient:
            raise ValueError("Apenas alimentos marcados como ingredientes podem ser adicionados")
        
        if ingredient in self._additional_ingredients:
            raise ValueError("Este ingrediente já foi adicionado")
        
        self._additional_ingredients.append(ingredient)
        # Atualizar restrições e calorias
        self._alimentary_restrictions.extend(ingredient.alimentary_restrictions)
        self._calories += ingredient.calories
    
    def remove_ingredient(self, ingredient: 'Alimento') -> None:
        """
        Remove um ingrediente do alimento.
        
        Atualiza corretamente calorias e restrições ao remover.
        
        Args:
            ingredient (Alimento): O ingrediente a remover
            
        Raises:
            ValueError: Se o ingrediente não estiver na lista
            
        Example:
            >>> burger.remove_ingredient(queijo)
        """
        if ingredient not in self._additional_ingredients:
            raise ValueError("Ingrediente não encontrado neste alimento")
        
        self._additional_ingredients.remove(ingredient)
        # Remover restrições e calorias
        self._alimentary_restrictions = [
            r for r in self._alimentary_restrictions 
            if r not in ingredient.alimentary_restrictions
        ]
        self._calories -= ingredient.calories
    
    def validar(self) -> bool:
        """
        Valida as regras de negócio do alimento.
        
        Returns:
            bool: True se válido (herdado + data de expiração válida)
        """
        return super().validar() and bool(self._expiration_date)
    
    def __repr__(self) -> str:
        """
        Representação em string do alimento.
        
        Returns:
            str: String formatada com informações do alimento
        """
        return f"{self.__class__.__name__}(name='{self._name}', price=R${self._price:.2f}, " \
               f"calories={self._calories}, expiration_date={self._expiration_date})"