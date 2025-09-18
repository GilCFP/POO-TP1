from Produto import Produto
from Alimento import Alimento


class Combo:
    def __init__(self, name:str, items:list[Produto]):
        self.name = name
        self.items = items
        self.price = sum(item.price for item in items)

    def apply_discount(self, discount):
        if 0 <= discount <= 1:
            self.price *= (1 - discount)
        else:
            raise ValueError("Discount must be between 0 and 1")
        
    def get_time_to_prepare(self):
        return sum(item.time_to_prepare for item in self.items if isinstance(item, Alimento))

    def __repr__(self):
        return f"Combo(name={self.name}, price={self.price:.2f}, items={self.items})"
