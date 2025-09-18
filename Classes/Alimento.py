from Produto import Produto
from RestricaoAlimentar import RestricaoAlimentar

class Alimento(Produto):
    def __init__(self, name:str, price:float, expiration_date:str, calories:int, time_to_prepare:int=0, available:bool=True, alimentary_restrictions:list[RestricaoAlimentar]=[], is_ingredient:bool=False):
        super().__init__(name, price, available)
        self.expiration_date = expiration_date
        self.calories = calories
        self.time_to_prepare = time_to_prepare
        self.alimentary_restrictions = alimentary_restrictions
        self.is_ingredient = is_ingredient
        self.additional_ingredients = []

    def is_expired(self, current_date:str):
        return current_date > self.expiration_date
    
    def add_ingredient(self, ingredient:"Alimento"):
        
        if self.is_ingredient:
            raise ValueError("Cannot add ingredients to an ingredient")
        
        if not ingredient.is_ingredient:
            raise ValueError("Ingredient must be marked as an ingredient")
        
        self.additional_ingredients.append(ingredient)
        self.alimentary_restrictions.extend(ingredient.alimentary_restrictions)
        self.calories += ingredient.calories
    
    def remove_ingredient(self, ingredient:"Alimento"):
        if ingredient in self.additional_ingredients:
            self.additional_ingredients.remove(ingredient)
            self.alimentary_restrictions = [r for r in self.alimentary_restrictions if r not in ingredient.alimentary_restrictions]
            self.calories -= ingredient.calories
        else:
            raise ValueError("Ingredient not found in the food item")
    
    def __repr__(self):
        
        return f"Food(name={self.name}, price={self.price:.2f}, expiration_date={self.expiration_date}, time_to_prepare={self.time_to_prepare})"