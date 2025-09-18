from Cliente import Cliente
from Pedido import Pedido


class Caixa:
    def __init__(self, initial_cash:float=0.0):
        self.total_revenue = initial_cash

    def process_payment(self, client:Cliente):
        order_total = client.cart.get_total()
        if client.balance >= order_total:
            client._remove_funds(order_total)
            self.total_revenue += order_total
            client.cart = Pedido()
        else:
            raise ValueError("Insufficient funds for payment")

    def __repr__(self):
        return f"CashRegister(total_revenue={self.total_revenue:.2f})"