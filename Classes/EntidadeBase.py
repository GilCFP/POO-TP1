"""
Módulo EntidadeBase: Define a classe abstrata base para todas as entidades do sistema.

Este módulo implementa o padrão de design Template Method, fornecendo uma base
comum para todas as classes do domínio com encapsulamento e validação.

Author: Desenvolvimento POO TP1
Date: 2024
"""

from abc import ABC, abstractmethod
from datetime import datetime


class EntidadeBase(ABC):
    """
    Classe abstrata base para todas as entidades do sistema de restaurante.
    
    Implementa encapsulamento, validação e comportamentos comuns a todas
    as entidades através de propriedades protegidas.
    
    Attributes:
        _id (int): Identificador único da entidade (protegido)
        _data_criacao (datetime): Data de criação da entidade (protegido)
    
    Example:
        class MinhaEntidade(EntidadeBase):
            def validar(self):
                return True
    """
    
    def __init__(self):
        """
        Inicializa a entidade base com ID único e timestamp de criação.
        """
        self._id = id(self)
        self._data_criacao = datetime.now()
    
    @property
    def id(self) -> int:
        """
        Obtém o identificador único da entidade.
        
        Returns:
            int: O ID da entidade (somente leitura)
        """
        return self._id
    
    @property
    def data_criacao(self) -> datetime:
        """
        Obtém a data de criação da entidade.
        
        Returns:
            datetime: A data e hora de criação (somente leitura)
        """
        return self._data_criacao
    
    @abstractmethod
    def validar(self) -> bool:
        """
        Método abstrato que deve ser implementado pelas subclasses.
        Valida as regras de negócio específicas da entidade.
        
        Returns:
            bool: True se a entidade é válida, False caso contrário
            
        Raises:
            NotImplementedError: Se não implementado na subclasse
        """
        pass
    
    def __repr__(self) -> str:
        """
        Representação em string da entidade.
        
        Returns:
            str: String com informações da entidade
        """
        return f"{self.__class__.__name__}(id={self._id})"
