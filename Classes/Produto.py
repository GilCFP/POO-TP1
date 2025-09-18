class Produto:
    def __init__(self, name:str, price, available:bool=True):
        self.name = name
        self.id = id(self)
        self.price = price
        self.available = available

    def apply_discount(self, discount):
        if 0 <= discount <= 1:
            self.price *= (1 - discount)
        else:
            raise ValueError("Discount must be between 0 and 1")

    def __repr__(self):
        return f"Product(name={self.name}, price={self.price:.2f})"