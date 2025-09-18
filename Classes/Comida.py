from typing import Optional

from .Alimento import Alimento
from .RestricaoAlimentar import RestricaoAlimentar


class Comida(Alimento):
    def __init__(self, name:str, price:float, expiration_date:str, calories:int, persons_served:int, time_to_prepare:int=0, available:bool=True, alimentary_restrictions:Optional[list[RestricaoAlimentar]]=None, is_ingredient:bool=False):
        if alimentary_restrictions is None:
            alimentary_restrictions = []
        super().__init__(name, price, expiration_date, calories, time_to_prepare, available, alimentary_restrictions, is_ingredient)
        self.persons_served = persons_served