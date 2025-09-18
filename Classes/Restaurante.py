from Produto import Produto
from Cliente import Cliente
from Caixa import Caixa


class Restaurante:
    def __init__(self, initial_cash:float=0.0):
        self.menu = []
        self.clients = []
        self.cash_register = Caixa(initial_cash)
        

    def add_product_to_menu(self, product:Produto):
        self.menu.append(product)

    def register_client(self, client:Cliente):
        self.clients.append(client)

    def __repr__(self):
        return f"Restaurant(menu={self.menu}, clients={self.clients}, cash_register={self.cash_register})"