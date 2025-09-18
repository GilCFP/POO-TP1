from Alimento import Alimento
from RestricaoAlimentar import RestricaoAlimentar



class Bebida(Alimento):
    def __init__(self, name:str, price:float, expiration_date:str, calories:int, volume_ml:int, is_alcoholic:bool, time_to_prepare:int=0, available:bool=True, alimentary_restrictions:list[RestricaoAlimentar]=[], is_ingredient:bool=False):
        super().__init__(name, price, expiration_date, calories, time_to_prepare, available, alimentary_restrictions)
        self.volume_ml = volume_ml
        self.is_alcoholic = is_alcoholic
        self.is_ingredient = is_ingredient