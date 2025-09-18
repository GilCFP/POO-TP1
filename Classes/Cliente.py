from RestricaoAlimentar import RestricaoAlimentar
from StatusPedido import StatusPedido
from Produto import Produto
from Alimento import Alimento
from Pedido import Pedido


class Cliente:
    
    def __init__(self, name:str, balance:float=0.0, cart:Pedido=None, address:str=None):
        self.name = name
        self.balance = balance
        self.cart = cart if cart is not None else Pedido()
        self.address = address
        self.alimentary_restrictions: list[RestricaoAlimentar] = []

    
    def add_alimentary_restriction(self, restriction:RestricaoAlimentar):
        if restriction not in self.alimentary_restrictions:
            self.alimentary_restrictions.append(restriction)

    def remove_alimentary_restriction(self, restriction:RestricaoAlimentar):
        if restriction in self.alimentary_restrictions:
            self.alimentary_restrictions.remove(restriction)

    def clear_alimentary_restrictions(self):
        self.alimentary_restrictions.clear()

    def can_consume(self, product:Produto):
        if isinstance(product, Alimento):
            for restriction in self.alimentary_restrictions:
                if restriction in product.alimentary_restrictions:
                    return False
        return True
    
    def _add_funds(self, amount:float):
        if amount > 0:
            self.balance += amount
        else:
            raise ValueError("Amount must be positive")
    
    def _remove_funds(self, amount:float):
        if 0 < amount <= self.balance:
            self.balance -= amount
        else:
            raise ValueError("Insufficient funds or invalid amount")
    
    def pay_cart(self):
        order_total = self.cart.get_total()
        if self.balance >= order_total:
            self._remove_funds(order_total)
            self.cart.change_status(StatusPedido.PENDING_PAYMENT)
        else:
            raise ValueError("Insufficient funds to pay for the cart")

    def __repr__(self):
        return f"Client(name={self.name}, balance={self.balance:.2f}, cart={self.cart})"